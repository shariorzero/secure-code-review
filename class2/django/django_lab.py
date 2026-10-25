"""
Django Secure Code Review Lab (একটি ফাইল, ইচ্ছাকৃতভাবে দুর্বল)
সেটআপ:  python django_lab.py migrate && python django_lab.py seed
চালান:   python django_lab.py runserver --noreload
⚠️ শুধু লোকাল/Codespaces-এ চালান। প্রোডাকশনে নয়।
"""
import sys
from django.conf import settings

settings.configure(
    DEBUG=True, SECRET_KEY="lab-only-not-a-real-secret", ROOT_URLCONF=__name__, ALLOWED_HOSTS=["*"],
    INSTALLED_APPS=["django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions"],
    MIDDLEWARE=["django.contrib.sessions.middleware.SessionMiddleware",
                "django.contrib.auth.middleware.AuthenticationMiddleware"],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "lab.sqlite3"}},
    TEMPLATES=[{"BACKEND": "django.template.backends.django.DjangoTemplates"}],
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
)
import django
django.setup()

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.template import Context, Template
from django.urls import path


# ---------- VULN 1: ORM injection (raw SQL-এ f-string) ----------
def search(request):
    q = request.GET.get("q", "")
    rows = User.objects.raw(f"SELECT * FROM auth_user WHERE username = '{q}'")
    return JsonResponse({"users": [u.username for u in rows]})


# ---------- VULN 2: |safe দিয়ে XSS ----------
def greet(request):
    name = request.GET.get("name", "")
    return HttpResponse(Template("<h1>Hello {{ name|safe }}</h1>").render(Context({"name": name})))


# ---------- VULN 3: ইউজারের লেখা টেমপ্লেট (SSTI) ----------
def preview(request):
    t = request.GET.get("t", "Hello {{ name }}")
    return HttpResponse(Template(t).render(Context({"name": "guest", "api_key": "sk-lab-12345"})))


# ---------- VULN 4: অথেনটিকেশন/অথরাইজেশন নেই ----------
def report(request):
    return JsonResponse({"report": "Q4 payroll: CONFIDENTIAL"})


# ======================= ইন্সট্রাক্টর সমাধান (/safe/...) =======================
def search_safe(request):
    q = request.GET.get("q", "")
    return JsonResponse({"users": [u.username for u in User.objects.filter(username=q)]})  # বা raw(..., [q])


def greet_safe(request):
    name = request.GET.get("name", "")
    return HttpResponse(Template("<h1>Hello {{ name }}</h1>").render(Context({"name": name})))  # autoescape চালু


def preview_safe(request):
    t = request.GET.get("t", "guest")
    return HttpResponse(Template("Hello {{ name }}").render(Context({"name": t})))  # ইউজার ডেটা, টেমপ্লেট নয়


@login_required
@user_passes_test(lambda u: u.is_staff)
def report_safe(request):
    return JsonResponse({"report": "Q4 payroll: CONFIDENTIAL"})


urlpatterns = [
    path("search", search), path("greet", greet), path("preview", preview), path("report", report),
    path("safe/search", search_safe), path("safe/greet", greet_safe),
    path("safe/preview", preview_safe), path("safe/report", report_safe),
]


def seed():
    User.objects.get_or_create(username="alice", defaults={"email": "alice@lab.local"})
    User.objects.get_or_create(username="bob", defaults={"email": "bob@lab.local"})
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@lab.local", "lab-admin-pass")
    print("seeded: alice, bob, admin")


if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    if sys.argv[1:2] == ["seed"]:
        seed()
    else:
        execute_from_command_line(sys.argv)
