from django import forms
from django.contrib.auth import password_validation

from .models import Profile, User


class StyledFormMixin:
    def apply_styles(self):
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check")
            else:
                field.widget.attrs.setdefault("class", "form-control")


class RegisterForm(StyledFormMixin, forms.ModelForm):
    password1 = forms.CharField(label="رمز عبور", widget=forms.PasswordInput)
    password2 = forms.CharField(label="تکرار رمز عبور", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username", "email", "phone", "first_name", "last_name")
        labels = {
            "username": "نام کاربری",
            "email": "ایمیل",
            "phone": "شماره تلفن",
            "first_name": "نام",
            "last_name": "نام خانوادگی",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()
        self.fields["email"].required = False
        self.fields["phone"].required = False

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("email") and not cleaned.get("phone"):
            raise forms.ValidationError("حداقل ایمیل یا شماره تلفن را وارد کن.")
        if cleaned.get("password1") != cleaned.get("password2"):
            self.add_error("password2", "تکرار رمز عبور یکسان نیست.")
        if cleaned.get("password1"):
            candidate = User(
                username=cleaned.get("username", ""),
                email=cleaned.get("email"),
                phone=cleaned.get("phone"),
                first_name=cleaned.get("first_name", ""),
                last_name=cleaned.get("last_name", ""),
            )
            password_validation.validate_password(cleaned["password1"], candidate)
        return cleaned

    def save(self, commit=True):
        user = User(
            username=self.cleaned_data["username"],
            email=self.cleaned_data.get("email") or None,
            phone=self.cleaned_data.get("phone") or None,
            first_name=self.cleaned_data.get("first_name", ""),
            last_name=self.cleaned_data.get("last_name", ""),
        )
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            Profile.objects.get_or_create(user=user)
        return user


class LoginForm(StyledFormMixin, forms.Form):
    identifier = forms.CharField(label="نام کاربری، ایمیل یا شماره تلفن")
    password = forms.CharField(label="رمز عبور", widget=forms.PasswordInput)
    remember_me = forms.BooleanField(label="مرا به خاطر بسپار", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()


class AccountForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone")
        labels = {"first_name": "نام", "last_name": "نام خانوادگی", "email": "ایمیل", "phone": "تلفن"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("email") and not cleaned.get("phone"):
            raise forms.ValidationError("حداقل ایمیل یا شماره تلفن باید باقی بماند.")
        return cleaned


class ProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("avatar", "bio", "city", "website")
        labels = {"avatar": "تصویر حساب", "bio": "درباره من", "city": "شهر", "website": "وب‌سایت"}
        widgets = {"bio": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()
