from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from .models import Resume, Skill


class ResumeFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="tester",
            email="tester@example.com",
            password="A-strong-password-123",
        )
        self.resume = Resume.objects.create(
            user=self.user,
            title="Backend CV",
            full_name="کاربر تست",
            job_title="Backend Developer",
            summary="خلاصه رزومه تست",
            email="tester@example.com",
        )
        Skill.objects.create(resume=self.resume, name="Django", percentage=85)

    def test_private_resume_is_hidden_from_anonymous_user(self):
        response = self.client.get(self.resume.get_absolute_url())
        self.assertEqual(response.status_code, 404)

    def test_owner_can_preview_private_resume(self):
        self.client.login(username="tester", password="A-strong-password-123")
        response = self.client.get(reverse("resumes:preview", kwargs={"pk": self.resume.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "کاربر تست")

    def test_public_resume_and_pdf(self):
        self.resume.status = Resume.Status.PUBLISHED
        self.resume.visibility = Resume.Visibility.PUBLIC
        self.resume.is_listed = True
        self.resume.save()
        page = self.client.get(self.resume.get_absolute_url())
        self.assertEqual(page.status_code, 200)
        pdf = self.client.get(reverse("resumes:pdf", kwargs={"slug": self.resume.slug}))
        self.assertEqual(pdf.status_code, 200)
        self.assertEqual(pdf["Content-Type"], "application/pdf")
        self.assertTrue(pdf.content.startswith(b"%PDF"))

    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse("resumes:dashboard"))
        self.assertEqual(response.status_code, 302)


class RegistrationTests(TestCase):
    def test_registration_requires_email_or_phone(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "email": "",
                "phone": "",
                "password1": "A-strong-password-123",
                "password2": "A-strong-password-123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())


class BuilderRegressionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="builder",
            email="builder@example.com",
            password="A-strong-password-123",
        )
        self.resume = Resume.objects.create(
            user=self.user,
            title="Builder CV",
            full_name="کاربر سازنده",
            email="builder@example.com",
        )
        self.client.login(username="builder", password="A-strong-password-123")

    @staticmethod
    def management(prefix, total, initial=0):
        return {
            f"{prefix}-TOTAL_FORMS": str(total),
            f"{prefix}-INITIAL_FORMS": str(initial),
            f"{prefix}-MIN_NUM_FORMS": "0",
            f"{prefix}-MAX_NUM_FORMS": "1000",
        }

    def test_positions_are_hidden_and_assigned_automatically(self):
        from .forms import LanguageForm, ProjectForm, SkillForm

        self.assertNotIn("position", SkillForm().fields)
        self.assertNotIn("position", LanguageForm().fields)
        self.assertNotIn("position", ProjectForm().fields)

        data = {}
        data.update(self.management("skill", 2))
        data.update(self.management("language", 0))
        data.update(self.management("soft_skill", 0))
        data.update(self.management("interest", 0))
        data.update(
            {
                "skill-0-name": "Python",
                "skill-0-category": "Backend",
                "skill-0-level": "advanced",
                "skill-0-percentage": "90",
                "skill-1-name": "Django",
                "skill-1-category": "Backend",
                "skill-1-level": "expert",
                "skill-1-percentage": "92",
            }
        )
        response = self.client.post(reverse("resumes:builder_skills", kwargs={"pk": self.resume.pk}), data)
        self.assertRedirects(response, reverse("resumes:builder_projects", kwargs={"pk": self.resume.pk}))
        self.assertEqual(list(self.resume.skills.values_list("position", flat=True)), [1, 2])

    def test_deleted_new_or_existing_skill_is_not_validated(self):
        skill = Skill.objects.create(resume=self.resume, name="Temporary")
        data = {}
        data.update(self.management("skill", 1, initial=1))
        data.update(self.management("language", 0))
        data.update(self.management("soft_skill", 0))
        data.update(self.management("interest", 0))
        data.update({"skill-0-id": str(skill.pk), "skill-0-DELETE": "on"})
        response = self.client.post(reverse("resumes:builder_skills", kwargs={"pk": self.resume.pk}), data)
        self.assertRedirects(response, reverse("resumes:builder_projects", kwargs={"pk": self.resume.pk}))
        self.assertFalse(self.resume.skills.exists())

    def test_project_section_can_be_completely_empty(self):
        data = {}
        data.update(self.management("project", 0))
        data.update(self.management("certificate", 0))
        data.update(self.management("social", 0))
        response = self.client.post(reverse("resumes:builder_projects", kwargs={"pk": self.resume.pk}), data)
        self.assertRedirects(response, reverse("resumes:builder_design", kwargs={"pk": self.resume.pk}))
        self.assertFalse(self.resume.projects.exists())

    def test_current_experience_clears_end_date_and_normalizes_persian_digits(self):
        data = self.management("experience", 1)
        data.update(
            {
                "experience-0-role": "برنامه‌نویس",
                "experience-0-company": "شرکت تست",
                "experience-0-location": "تهران",
                "experience-0-start_date": "۱۴۰۳/۰۲/۰۵",
                "experience-0-end_date": "۱۴۰۴/۰۱/۰۱",
                "experience-0-is_current": "on",
                "experience-0-description": "در حال همکاری",
            }
        )
        response = self.client.post(reverse("resumes:builder_experience", kwargs={"pk": self.resume.pk}), data)
        self.assertRedirects(response, reverse("resumes:builder_education", kwargs={"pk": self.resume.pk}))
        item = self.resume.experiences.get()
        self.assertEqual(item.start_date, "1403/02/05")
        self.assertEqual(item.end_date, "")
        self.assertTrue(item.is_current)
        self.assertEqual(item.position, 1)

    def test_education_grade_must_be_between_zero_and_twenty(self):
        data = self.management("education", 1)
        data.update(
            {
                "education-0-degree": "کارشناسی",
                "education-0-field": "کامپیوتر",
                "education-0-institution": "دانشگاه تست",
                "education-0-location": "تهران",
                "education-0-start_date": "1400/07/01",
                "education-0-end_date": "1404/04/01",
                "education-0-grade": "20.01",
                "education-0-description": "",
            }
        )
        response = self.client.post(reverse("resumes:builder_education", kwargs={"pk": self.resume.pk}), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "معدل باید حداکثر ۲۰ باشد")
        self.assertFalse(self.resume.educations.exists())

    def test_education_grade_accepts_persian_digits(self):
        data = self.management("education", 1)
        data.update(
            {
                "education-0-degree": "کارشناسی",
                "education-0-field": "کامپیوتر",
                "education-0-institution": "دانشگاه تست",
                "education-0-location": "تهران",
                "education-0-start_date": "۱۴۰۰/۰۷/۰۱",
                "education-0-end_date": "۱۴۰۴/۰۴/۰۱",
                "education-0-grade": "۱۹٫۷۵",
                "education-0-description": "",
            }
        )
        response = self.client.post(reverse("resumes:builder_education", kwargs={"pk": self.resume.pk}), data)
        self.assertRedirects(response, reverse("resumes:builder_skills", kwargs={"pk": self.resume.pk}))
        self.assertEqual(str(self.resume.educations.get().grade), "19.75")


class CompleteResumeContentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="complete", email="complete@example.com", password="A-strong-password-123")
        self.resume = Resume.objects.create(
            user=self.user,
            full_name="رزومه کامل",
            birth_date="1379/11/06",
            marital_status=Resume.MaritalStatus.SINGLE,
            military_status=Resume.MilitaryStatus.COMPLETED,
            status=Resume.Status.PUBLISHED,
            visibility=Resume.Visibility.PUBLIC,
        )

    def test_readable_jalali_date_and_new_sections_render(self):
        from .models import Experience, Interest, SoftSkill
        Experience.objects.create(
            resume=self.resume,
            role="برنامه‌نویس",
            company="شرکت",
            start_date="1403/08/01",
            is_current=True,
            achievements="طراحی API\nکاهش زمان پاسخ",
        )
        SoftSkill.objects.create(resume=self.resume, name="حل مسئله")
        Interest.objects.create(resume=self.resume, name="موسیقی")
        response = self.client.get(self.resume.get_absolute_url())
        self.assertContains(response, "آبان ۱۴۰۳ تا اکنون")
        self.assertContains(response, "وظایف و دستاوردها")
        self.assertContains(response, "مهارت‌های نرم")
        self.assertContains(response, "علاقه‌مندی‌ها")

    def test_birth_date_is_human_readable(self):
        self.assertEqual(self.resume.birth_date_display, "۶ بهمن ۱۳۷۹")
