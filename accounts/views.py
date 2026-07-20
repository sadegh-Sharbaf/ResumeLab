from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import AccountForm, LoginForm, ProfileForm, RegisterForm
from .models import Profile


def register_view(request):
    if request.user.is_authenticated:
        return redirect("resumes:dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user, backend="accounts.backends.IdentifierBackend")
        messages.success(request, "حساب ساخته شد؛ حالا اولین رزومه‌ات را بساز.")
        return redirect("resumes:create")
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("resumes:dashboard")
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["identifier"],
            password=form.cleaned_data["password"],
        )
        if user:
            login(request, user)
            if not form.cleaned_data["remember_me"]:
                request.session.set_expiry(0)
            messages.success(request, "خوش آمدی.")
            next_url = request.GET.get("next")
            return redirect(next_url or reverse("resumes:dashboard"))
        form.add_error(None, "اطلاعات ورود صحیح نیست.")
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.info(request, "از حساب خارج شدی.")
    return redirect("personalapp:home")


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    account_form = AccountForm(request.POST or None, instance=request.user, prefix="account")
    profile_form = ProfileForm(request.POST or None, request.FILES or None, instance=profile, prefix="profile")
    if request.method == "POST" and account_form.is_valid() and profile_form.is_valid():
        account_form.save()
        profile_form.save()
        messages.success(request, "تنظیمات حساب ذخیره شد.")
        return redirect("accounts:profile")
    return render(
        request,
        "accounts/profile.html",
        {"account_form": account_form, "profile_form": profile_form},
    )
