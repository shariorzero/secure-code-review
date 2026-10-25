# Module 17: Secure Code Review Lab (Class 1: Flask, Class 2: Node.js ও Django)

> ⚠️ এখানকার অনেক কোড **ইচ্ছাকৃতভাবে দুর্বল**। শুধু লোকাল বা Codespaces-এ চালান, কখনো পাবলিক সার্ভারে নয়।

## ফোল্ডার স্ট্রাকচার

```
.
├── vulnerable/app.py            # Class 1: দুর্বল Flask অ্যাপ (ইন্সট্রাক্টর ডেমো)
├── fixed/app.py                 # Class 1: সমাধান (FIX 1..6 কমেন্টসহ)
├── student/app.py               # Class 1: শিক্ষার্থীদের ফাইল (# RED FLAG মার্কার ও # TODO সহ, safe_eval তৈরি)
├── student/app_unmarked.py      # মার্কার ছাড়া কপি (শূন্য থেকে খুঁজতে চাইলে)
├── challenge/app.py             # Class 1: কুইক হান্টিং চ্যালেঞ্জ (/ping, /hello)
├── challenge/fixed_app.py       # চ্যালেঞ্জের সমাধান (ইন্সট্রাক্টর)
├── class1-gui/                  # ব্রাউজার GUI: ফর্মে ইনপুট দিয়ে প্রতিটি রুট পরীক্ষা (README ভেতরে)
├── helpers/safe_eval.py         # Class 1 ল্যাব খ-এর helper
├── tests/test_security.py       # Class 1 প্যাচ যাচাই
├── rules/class1-flask.yml       # কাস্টম Semgrep রুল
├── tools/forge_cookie.py        # ইন্সট্রাক্টর ডেমো (ঐচ্ছিক)
├── class2/
│   ├── node/pp_lab.js           # Prototype Pollution ল্যাব
│   ├── node/pp_fixed.js         # সমাধান
│   ├── node/instructor_pp_bypass.js  # কোন ফিক্স কোন payload-এ ভাঙে (AI-ফিক্স যাচাইয়ের ডেমো)
│   ├── audit-lab/               # npm audit ল্যাব
│   ├── reading-only/            # ম্যানুয়াল package.json পড়ার অনুশীলন (ইনস্টল করবেন না)
│   ├── dvwa-takehome/           # ঐচ্ছিক টেক-হোম: DVWA-র SQLi সোর্স তুলনা (৫ লাইনের ছক)
│   └── django/
│       ├── django_lab_student.py  # শিক্ষার্থীদের জন্য (# RED FLAG মার্কার ও # TODO সহ)
│       ├── verify_student.py      # শিক্ষার্থীর ফিক্স যাচাই (শুরুতে FAIL, ঠিক করলে PASS)
│       ├── django_lab.py          # ইন্সট্রাক্টরের জন্য (/safe/... সমাধানসহ)
│       └── verify.py              # ইন্সট্রাক্টর যাচাই
├── scripts/verify_labs.sh       # সব ল্যাব একবারে যাচাই
├── .github/workflows/           # semgrep.yml, codeql.yml
├── .devcontainer/               # Codespaces (Python, Node, ping)
├── .env.example
├── LAB_GUIDE.md                 # Class 1 ধাপে ধাপে গাইড
└── requirements.txt
```

## ক্লাসের আগে (ইন্সট্রাক্টর): এক কমান্ডে সব যাচাই

```bash
pip install -r requirements.txt
bash scripts/verify_labs.sh
```

প্রত্যাশিত: Class 1 `fixed` সব পাস, `vulnerable`-এ ৬টি ফেল (বাগের প্রমাণ), চ্যালেঞ্জ ও Node ল্যাব ঠিকমতো দেখায়, Django-র ৮টি চেকই `PASS`।

## Class 1 (Flask)

```bash
python vulnerable/app.py                 # http://localhost:5000 (ডেমো)
cp student/app_unmarked.py student/app.py   # শুধু মার্কার ছাড়া ফাইল চাইলে (ল্যাব ক শূন্য থেকে)
TARGET=student pytest -q                 # শিক্ষার্থীর প্যাচ যাচাই (ঐচ্ছিক)

# কুইক হান্টিং চ্যালেঞ্জ (vulnerable অ্যাপ বন্ধ রেখে)
FLASK_APP=challenge/app.py flask run
```

fixed অ্যাপ চালাতে: `cp .env.example .env && set -a && source .env && set +a && python fixed/app.py`

## Class 2 (Node.js ও Django)

```bash
# Prototype Pollution
node class2/node/pp_lab.js          # newUser.isAdmin = true (বাগ)
node class2/node/pp_fixed.js        # undefined (ঠিক)

# npm audit
cd class2/audit-lab && npm install --package-lock-only --ignore-scripts && npm audit

# Django (শিক্ষার্থীদের ফাইল)
cd class2/django
python django_lab_student.py migrate && python django_lab_student.py seed
python django_lab_student.py runserver --noreload    # http://localhost:8000
python verify_student.py                             # ফিক্স যাচাই: ঠিক করার পর সব PASS
```

## ক্লাসের আগে মনে রাখুন
- [ ] Codespaces-এ রিপো খুলে `bash scripts/verify_labs.sh` চালান
- [ ] `ping` ইনস্টল আছে কিনা দেখুন (`.devcontainer` নিজেই চেষ্টা করে)
- [ ] `semgrep` ও `npm audit`-এর ফল নিজে একবার দেখে নিন (ফল সময়ের সাথে বদলায়)
- [ ] CodeQL-এর জন্য রিপো GitHub-এ পুশ করে একবার ওয়ার্কফ্লো চালিয়ে রাখুন
- [ ] ক্লাসের পরিকল্পনা ও টকিং পয়েন্ট দেখুন লেসন প্ল্যান ডকে ("এপিসোড-স্টাইল সংস্করণ")
