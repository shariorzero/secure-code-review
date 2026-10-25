#!/usr/bin/env bash
# ইন্সট্রাক্টরের জন্য: ক্লাসের আগে সব ল্যাব একবারে যাচাই। রিপোর রুট থেকে: bash scripts/verify_labs.sh
set -u
echo "== Class 1: fixed অ্যাপ (সব PASS হওয়ার কথা) =="
TARGET=fixed python -m pytest -q tests 2>&1 | tail -2
echo "== Class 1: vulnerable অ্যাপ (৬টি FAIL হওয়াই প্রত্যাশিত) =="
TARGET=vulnerable python -m pytest -q tests 2>&1 | tail -2
echo "== Class 1 চ্যালেঞ্জ =="
python - << 'PY'
import importlib.util
def load(p):
    s = importlib.util.spec_from_file_location("m", p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
v = load("challenge/app.py").app.test_client(); f = load("challenge/fixed_app.py").app.test_client()
print("vuln /ping injection runs id :", "uid=" in v.get("/ping", query_string={"host": "127.0.0.1; id"}).get_data(as_text=True))
print("vuln /hello reflects script  :", "<script>" in v.get("/hello", query_string={"name": "<script>"}).get_data(as_text=True))
print("fixed /ping blocks injection :", f.get("/ping", query_string={"host": "127.0.0.1; id"}).status_code == 400)
print("fixed /hello escapes         :", "&lt;script&gt;" in f.get("/hello", query_string={"name": "<script>"}).get_data(as_text=True))
PY
echo "== Class 2: Node =="
node class2/node/pp_lab.js
node class2/node/pp_fixed.js
node class2/node/instructor_pp_bypass.js
echo "== Class 2: Django =="
( cd class2/django && python django_lab.py migrate >/dev/null 2>&1 && python django_lab.py seed && python verify.py \
  && echo '-- শিক্ষার্থীর ফাইল (শুরুতে ৪টি FAIL প্রত্যাশিত) --' && (python verify_student.py || true) )
rm -f class2/django/lab.sqlite3
