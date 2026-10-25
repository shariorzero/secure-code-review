"""শিক্ষার্থীর (বা ইন্সট্রাক্টরের) ফিক্স যাচাই:
    python class2/django/verify_student.py [ফাইলের পথ]      (আগে migrate ও seed চালান)
শুরুতে সবগুলো FAIL আসা স্বাভাবিক। ঠিক করার পর সবগুলো PASS হওয়া উচিত।
কার্যকারিতাও যাচাই হয়: ফিক্সের পর অ্যাপ যেন ভেঙে না যায়।"""
import importlib.util, os, sys

path = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "django_lab_student.py"))
os.chdir(os.path.dirname(path))
sys.argv = ["x"]
spec = importlib.util.spec_from_file_location("lab_target", path)
m = importlib.util.module_from_spec(spec); sys.modules["lab_target"] = m; spec.loader.exec_module(m)
from django.test import Client

c = Client()
def get(u, **p):
    r = c.get(u, p); return r.status_code, r.content.decode()

ok = True
def check(name, cond):
    global ok; ok &= bool(cond); print(("PASS " if cond else "FAIL ") + name)

check("search: ORM injection বন্ধ (RED FLAG 3)", "bob" not in get("/search", q="x' OR '1'='1")[1])
check("search: স্বাভাবিক সার্চ এখনো কাজ করে", "alice" in get("/search", q="alice")[1])
check("greet: |safe দিয়ে XSS বন্ধ (RED FLAG 4a)", "<script>" not in get("/greet", name="<script>")[1])
check("preview: টেমপ্লেট injection বন্ধ (RED FLAG 4b)", "sk-lab-12345" not in get("/preview", t="{{ api_key }}")[1])
check("report: লগইন ছাড়া 200 নয় (RED FLAG 5)", get("/report")[0] != 200)
sys.exit(0 if ok else 1)
