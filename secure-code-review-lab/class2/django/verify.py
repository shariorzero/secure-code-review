"""ইন্সট্রাক্টর যাচাই: python class2/django/verify.py  (আগে migrate ও seed চালান)
দুর্বল রুটে বাগ আছে এবং /safe/ রুটে নেই, তা প্রমাণ করে।"""
import importlib.util, os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.argv = ["x"]
spec = importlib.util.spec_from_file_location("django_lab", "django_lab.py")
m = importlib.util.module_from_spec(spec); sys.modules["django_lab"] = m; spec.loader.exec_module(m)
from django.test import Client

c = Client()
def get(u, **p):
    r = c.get(u, p); return r.status_code, r.content.decode()
ok = True
def check(name, cond):
    global ok; ok &= bool(cond); print(("PASS " if cond else "FAIL ") + name)

check("vuln search leaks all users", "bob" in get("/search", q="x' OR '1'='1")[1])
check("safe search blocks it",       "bob" not in get("/safe/search", q="x' OR '1'='1")[1])
check("vuln greet reflects <script>", "<script>" in get("/greet", name="<script>")[1])
check("safe greet escapes",           "&lt;script&gt;" in get("/safe/greet", name="<script>")[1])
check("vuln preview leaks api_key",   "sk-lab-12345" in get("/preview", t="{{ api_key }}")[1])
check("safe preview does not",        "sk-lab-12345" not in get("/safe/preview", t="{{ api_key }}")[1])
check("vuln report open to anonymous", get("/report")[0] == 200)
check("safe report redirects anonymous", get("/safe/report")[0] == 302)
sys.exit(0 if ok else 1)
