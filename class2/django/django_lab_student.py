"""
Class 2 ল্যাবের ফাইল: django_lab_student.py
  ল্যাব ক: প্রতিটি `# RED FLAG` মার্কারের পাশে ৩টি প্রশ্নের উত্তর লিখুন
            (ইনপুট কোথা থেকে? বিপজ্জনক জায়গা কোনটি? মাঝখানে পাহারা আছে কি?)
  ল্যাব খ: `# TODO` অনুযায়ী ঠিক করুন, তারপর একই curl কমান্ড আবার চালিয়ে যাচাই করুন।
  (RED FLAG 1 ও 2 Node.js ও package.json-এর, তাই এই ফাইলে নেই)
সেটআপ:  python django_lab_student.py migrate && python django_lab_student.py seed
চালান:   python django_lab_student.py runserver --noreload   (http://localhost:8000)
⚠️ ইচ্ছাকৃতভাবে দুর্বল। শুধু লোকাল/Codespaces-এ চালান।
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

from django.contrib.auth.decorators import login_required, user_passes_test  # RED FLAG 5 ঠিক করতে লাগবে
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.template import Context, Template
from django.urls import path


# RED FLAG 3: .raw( + f-string | ইনপুট: ____ | বিপজ্জনক জায়গা: ____ | পাহারা: ____
# TODO (ল্যাব খ): ORM-এর নিজের পদ্ধতি ব্যবহার করুন, নিজে SQL স্ট্রিং জোড়া দেবেন না
# যাচাই: curl -s -G localhost:8000/search --data-urlencode "q=x' OR '1'='1"
def search(request):
    q = request.GET.get("q", "")
    rows = User.objects.raw(f"SELECT * FROM auth_user WHERE username = '{q}'")
    return JsonResponse({"users": [u.username for u in rows]})


# RED FLAG 4a: |safe | ইনপুট: ____ | বিপজ্জনক জায়গা: ____ | পাহারা: ____
# TODO (ল্যাব খ): Django-র ডিফল্ট সুরক্ষা আবার চালু করুন
# যাচাই: curl -s -G localhost:8000/greet --data-urlencode "name=<b>x</b>"
def greet(request):
    name = request.GET.get("name", "")
    return HttpResponse(Template("<h1>Hello {{ name|safe }}</h1>").render(Context({"name": name})))


# RED FLAG 4b: Template( + ইউজারের ইনপুট | ইনপুট: ____ | বিপজ্জনক জায়গা: ____ | পাহারা: ____
# TODO (ল্যাব খ): টেমপ্লেট স্থির রাখুন, ইউজারের লেখা শুধু ভেরিয়েবলের মান হবে
# যাচাই: curl -s -G localhost:8000/preview --data-urlencode "t={{ api_key }}"
def preview(request):
    t = request.GET.get("t", "Hello {{ name }}")
    return HttpResponse(Template(t).render(Context({"name": "guest", "api_key": "sk-lab-12345"})))


# RED FLAG 5: ডেকোরেটর নেই | লগইন (authentication) আছে? অনুমতি (authorization) আছে? ____
# TODO (ল্যাব খ): লগইন ও স্টাফ-অনুমতি, দুটোই চেক করুন
# যাচাই: curl -i localhost:8000/report  (200 নয়, 302 আসা উচিত)
def report(request):
    return JsonResponse({"report": "Q4 payroll: CONFIDENTIAL"})


urlpatterns = [
    path("search", search), path("greet", greet), path("preview", preview), path("report", report),
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
