import base64
import mimetypes
import os
import shutil
from pathlib import Path

from django.conf import settings
from django.template.loader import render_to_string


class PDFGenerationError(RuntimeError):
    pass


def _avatar_data_uri(resume):
    if not resume.avatar:
        return ""
    try:
        with resume.avatar.open("rb") as image:
            payload = base64.b64encode(image.read()).decode("ascii")
        mime = mimetypes.guess_type(resume.avatar.name)[0] or "image/jpeg"
        return f"data:{mime};base64,{payload}"
    except (OSError, ValueError):
        return ""


def _browser_candidates():
    configured = os.getenv("CHROME_BIN", "").strip()
    if configured:
        yield configured

    for name in (
        "chromium",
        "chromium-browser",
        "google-chrome",
        "google-chrome-stable",
        "microsoft-edge",
        "msedge",
    ):
        executable = shutil.which(name)
        if executable:
            yield executable

    if os.name == "nt":
        roots = [
            os.getenv("PROGRAMFILES", ""),
            os.getenv("PROGRAMFILES(X86)", ""),
            os.getenv("LOCALAPPDATA", ""),
        ]
        relative_paths = [
            Path("Google/Chrome/Application/chrome.exe"),
            Path("Microsoft/Edge/Application/msedge.exe"),
            Path("Chromium/Application/chrome.exe"),
        ]
        for root in roots:
            if not root:
                continue
            for relative in relative_paths:
                candidate = Path(root) / relative
                if candidate.exists():
                    yield str(candidate)


def find_browser():
    for candidate in _browser_candidates():
        if candidate and Path(candidate).exists():
            return candidate
    raise PDFGenerationError(
        "مرورگر Chrome/Edge/Chromium پیدا نشد. Chrome یا Edge را نصب کن یا مسیر آن را در CHROME_BIN قرار بده."
    )


def build_resume_pdf(resume) -> bytes:
    """Generate PDF from the exact same resume markup and CSS shown online."""
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise PDFGenerationError("پکیج Playwright نصب نیست؛ requirements.txt را دوباره نصب کن.") from exc

    css_path = settings.BASE_DIR / "base" / "static" / "css" / "resume.css"
    try:
        pdf_css = css_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PDFGenerationError(f"فایل استایل رزومه خوانده نشد: {exc}") from exc

    html = render_to_string(
        "resumes/pdf_resume.html",
        {
            "resume": resume,
            "avatar_uri": _avatar_data_uri(resume),
            "pdf_css": pdf_css,
            "pdf_mode": True,
        },
    )
    executable = find_browser()

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                executable_path=executable,
                args=["--no-sandbox", "--disable-dev-shm-usage", "--no-zygote"],
            )
            page = browser.new_page(viewport={"width": 1240, "height": 1754}, device_scale_factor=1)
            page.set_content(html, wait_until="load", timeout=60000)
            page.emulate_media(media="print")
            payload = page.pdf(
                format="A4",
                print_background=True,
                prefer_css_page_size=True,
                display_header_footer=False,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            )
            browser.close()
    except PlaywrightError as exc:
        raise PDFGenerationError(f"مرورگر نتوانست PDF را بسازد: {exc}") from exc

    if not payload.startswith(b"%PDF"):
        raise PDFGenerationError("خروجی مرورگر یک فایل PDF معتبر نیست.")
    return payload
