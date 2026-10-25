# ল্যাব গাইড: Flask Secure Code Review (ম্যানুয়াল আগে, টুল পরে)

**নিয়ম:** প্রতিটি বাগে এই তিন ধাপ: **১) এক্সপ্লয়ট করে দেখা → ২) কোড লাইন ধরে রিভিউ → ৩) নিজে প্যাচ লেখা।**
AI/SAST টুল এই ল্যাবের শেষ অংশে, ম্যানুয়াল কাজ শেষ হওয়ার পরে।

## ধাপ ০: সেটআপ

```bash
pip install -r requirements.txt
python vulnerable/app.py
```

আরেকটি টার্মিনালে:

```bash
curl -s localhost:5000/
curl -s -X POST localhost:5000/login -H 'Content-Type: application/json' \
     -d '{"username":"alice","password":"alice123"}' -i
```

## বাগ ম্যাপ (ইন্সট্রাক্টরের জন্য)

| # | বাগ | কোথায় | ঝুঁকি |
|---|---|---|---|
| 1 | `eval()` | `/calc` | Remote Code Execution |
| 2 | `exec()` | `/run` | Remote Code Execution |
| 3 | `debug=True`, `host=0.0.0.0` | `app.run(...)` | Werkzeug debugger এক্সপোজার, সোর্স কোড লিক |
| 4 | হার্ডকোড `secret_key` | অ্যাপের শুরুতে | সেশন কুকি ফোর্জ → privilege escalation |
| 5 | কুকি ফ্ল্যাগ বন্ধ | `app.config` | XSS দিয়ে কুকি চুরি, HTTP-তে কুকি লিক |
| 6 | CORS `*` + credentials | `CORS(...)` | যেকোনো সাইট থেকে ইউজারের ডেটা পড়ার সুযোগ |
| বোনাস | প্লেইনটেক্সট পাসওয়ার্ড, error message লিক | `USERS`, `/calc` | তথ্য ফাঁস |

---

## বাগ ১: `eval()` → RCE

**বুঝিয়ে বলার উপমা:** `eval()` হলো এমন একজন কর্মী যে কাগজে যা লেখা থাকে চোখ বন্ধ করে তা-ই করে ফেলে। কাগজে "২+২ কত?" লিখলে ঠিক আছে, কিন্তু "সেফের তালা খুলে দাও" লিখলেও সে করবে।

**এক্সপ্লয়ট (ধাপে ধাপে):**

```bash
# ১. স্বাভাবিক ব্যবহার
curl -s -G localhost:5000/calc --data-urlencode "expr=2+2"

# ২. পাইথন ফাংশন চলছে কিনা
curl -s -G localhost:5000/calc --data-urlencode "expr=__import__('os').getcwd()"

# ৩. সিস্টেম কমান্ড (প্রমাণ যে সার্ভারের ওপর নিয়ন্ত্রণ আছে)
curl -s -G localhost:5000/calc --data-urlencode "expr=__import__('os').popen('id').read()"
```

**রিভিউ প্রশ্ন (শিক্ষার্থীদের আগে ভাবতে দিন):**
1. ইউজারের ইনপুট কোন লাইনে ঢুকছে? (`request.args.get`)
2. সেই ইনপুট কোন লাইনে গিয়ে বিপজ্জনক ফাংশনে পৌঁছাচ্ছে? (`eval(expr)`) → একে বলে **source → sink**
3. `except` ব্লকে `error: {e}` কেন সমস্যা?

**প্যাচ কোন পথে ভাবতে হবে:** "ইনপুট ফিল্টার করবো" নয়, বরং "ইনপুট কখনো কোড হিসেবে চলবেই না।" ব্লকলিস্ট (`import` শব্দ আটকানো) কেন যথেষ্ট না তা আলোচনা করুন। হিন্ট: `ast` মডিউল, শুধু সংখ্যা ও `+ - * /`।

---

## বাগ ২: `exec()` → RCE

```bash
curl -s -X POST localhost:5000/run -H 'Content-Type: application/json' \
     -d '{"code":"result = 40 + 2"}'

curl -s -X POST localhost:5000/run -H 'Content-Type: application/json' \
     -d '{"code":"import os\nresult = os.listdir(\".\")"}'
```

**আলোচনা:** `exec`-এর সাথে `scope = {}` দিলেই কি নিরাপদ? (না। `import` তখনও কাজ করে।) "প্লাগিন/ফর্মুলা সুবিধা" দেওয়ার নিরাপদ বিকল্প কী? → allowlist করা নামকরা অপারেশন (`fixed/app.py`-এর `ALLOWED_OPS`)।

---

## বাগ ৩: Debug mode ও Werkzeug debugger

**এক্সপ্লয়ট/পর্যবেক্ষণ:**

```bash
# ইচ্ছাকৃত exception: ব্রাউজারে http://localhost:5000/boom খুলুন
curl -s localhost:5000/boom | head -40
```

ব্রাউজারে যা দেখাবেন:
- পুরো stack trace ও **সোর্স কোডের লাইন** (অ্যাটাকারের জন্য রিকন)
- প্রতিটি ফ্রেমে ইন্টারঅ্যাকটিভ কনসোল (PIN চায়)
- `http://localhost:5000/console` পেজ আলাদা করে খোলা যায়

**বুঝিয়ে বলুন (ধারণাগতভাবে):**
- debugger কনসোল মানে সার্ভারে সরাসরি পাইথন চালানো। এটা PIN দিয়ে সুরক্ষিত, কিন্তু PIN-টি মেশিনের কিছু বৈশিষ্ট্য থেকে তৈরি হয়। বাস্তবে অন্য কোনো বাগ (যেমন ফাইল রিড) থাকলে সেই তথ্য পাওয়া গেলে PIN অনুমান করা সম্ভব। তাই "PIN আছে, সমস্যা নেই" বলা ভুল ধারণা।
- `host="0.0.0.0"` মানে নেটওয়ার্কের সবাই পৌঁছাতে পারে (Codespaces-এ পোর্ট ফরওয়ার্ড হলে আরও সহজ)।

**প্যাচ:** `debug=True` বাদ, `host="127.0.0.1"`, প্রোডাকশনে `gunicorn`। ডেভেলপমেন্টে দরকার হলে `FLASK_DEBUG` এনভায়রনমেন্ট ভ্যারিয়েবল, কিন্তু কোডে হার্ডকোড নয়।

---

## বাগ ৪ ও ৫: হার্ডকোড secret ও দুর্বল কুকি

**ধাপ ১ – কুকির ফ্ল্যাগ দেখুন:**

```bash
curl -si -X POST localhost:5000/login -H 'Content-Type: application/json' \
     -d '{"username":"alice","password":"alice123"}' | grep -i set-cookie
```
`HttpOnly`, `Secure`, `SameSite` কোনোটাই নেই। এগুলো কী কাজ করে সেটা শিক্ষার্থীদের নিজেদের বলতে দিন।

**ধাপ ২ – কুকির ভেতরে কী আছে:** কুকির প্রথম অংশ (`.`-এর আগে) base64। ডিকোড করলে `{"role":"user","user":"alice"}` দেখা যায়। মূল শিক্ষা: **Flask সেশন কুকি সাইন করা, এনক্রিপ্ট করা নয়।**

**ধাপ ৩ – ফোর্জ (ইন্সট্রাক্টর ডেমো):** secret সোর্স কোডে দেখা গেলে অ্যাটাকার নিজেই কুকি বানাতে পারে।

```bash
COOKIE=$(python tools/forge_cookie.py)
curl -s -b "session=$COOKIE" localhost:5000/admin
# => {"secret_report": "Q4 financials: CONFIDENTIAL"}
```

**আলোচনা:** GitHub-এ secret কমিট হয়ে গেলে কী করতে হবে? (secret বদলানো/rotate করা, শুধু ফাইল থেকে মুছলে হবে না, কারণ git history-তে থেকে যায়।)

**প্যাচ:** `os.environ["SECRET_KEY"]`, `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_SAMESITE="Lax"`।

---

## বাগ ৬: CORS `*` + credentials

```bash
curl -si localhost:5000/ -H 'Origin: https://evil.example' | grep -i access-control
```
আউটপুটে `Access-Control-Allow-Origin: https://evil.example` ও `Access-Control-Allow-Credentials: true` আসবে। অর্থাৎ অ্যাপ বলছে, "যেকোনো সাইট ইউজারের লগইন কুকি সহ আমাকে রিকোয়েস্ট করতে পারে।"

**উপমা:** অফিসের সিকিউরিটি গার্ড যদি বলে, "যে কেউ নাম বললেই ভেতরে ঢুকতে পারবে, আর ঢুকলে কর্মচারীর পরিচয়পত্রও ব্যবহার করতে পারবে।"

**প্যাচ:** স্পষ্ট allowlist (`ALLOWED_ORIGINS`)। `*` ও `supports_credentials=True` একসাথে কখনো নয়।

---

## প্যাচ লেখার পর যাচাই

```bash
# student/app.py প্যাচ করুন, তারপর:
TARGET=student pytest -q
```

| টেস্ট | কোন বাগ |
|---|---|
| `test_eval_rce_blocked`, `test_calc_still_works` | ১ (কার্যকারিতা ঠিক রেখে) |
| `test_exec_blocked` | ২ |
| `test_debug_not_enabled` | ৩ |
| `test_forged_admin_cookie_rejected` | ৪ |
| `test_cookie_flags` | ৫ |
| `test_cors_not_open` | ৬ |

> `student/app.py` প্যাচ করলে `os.environ[...]` ব্যবহারের জন্য `.env` লোড করতে হবে (README দেখুন)। টেস্ট নিজে ডিফল্ট মান সেট করে নেয়।

---

## শেষ অংশ: একই অ্যাপে অটোমেশন (ক্লাসের শেষ ২৫–৩০%)

ম্যানুয়ালি যা ধরেছেন, টুল কতটা ধরল তুলনা করুন:

```bash
# Semgrep: আমাদের কাস্টম রুল + কমিউনিটি রুল
semgrep scan --config rules/class1-flask.yml vulnerable/
semgrep scan --config p/python --config p/flask vulnerable/
```

তুলনার প্রশ্ন: কোন বাগ টুল ধরল, কোনটা মিস করল? (যেমন CORS ও লজিক-ধাঁচের সমস্যা সাধারণত রুল দিয়ে সহজে ধরা পড়ে না, আর প্রতিটি টুলের ফলাফল আলাদা হতে পারে। তাই নিজে চালিয়ে দেখে ক্লাসে আলোচনা করুন।)

CI/CD: `.github/workflows/semgrep.yml` ও `codeql.yml` রিপোতে পুশ করলে PR-এ স্ক্যান চলবে। AI অ্যাসিস্ট্যান্টের দেওয়া fix `TARGET=... pytest -q` দিয়ে যাচাই করুন। AI যা বলে তা-ই নিরাপদ নয়।
