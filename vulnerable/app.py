"""
⚠️  INTENTIONALLY VULNERABLE — শুধুমাত্র ক্লাস/ল্যাবের জন্য।
এই কোড কখনো ইন্টারনেটে বা প্রোডাকশনে ডিপ্লয় করবেন না।

ল্যাবের বাগ ম্যাপ (শিক্ষার্থীদের কাছে প্রথমে এই কমেন্টগুলো লুকিয়ে দিতে পারেন):
  BUG 1: eval()          -> RCE
  BUG 2: exec()          -> RCE
  BUG 3: debug=True      -> Werkzeug debugger এক্সপোজার
  BUG 4: hardcoded secret_key -> সেশন কুকি ফোর্জ
  BUG 5: insecure cookie flags
  BUG 6: CORS wildcard + credentials
  BONUS: plaintext পাসওয়ার্ড, error message leak
"""
from flask import Flask, request, jsonify, session
from flask_cors import CORS

app = Flask(__name__)

# BUG 4: সিক্রেট সোর্স কোডে হার্ডকোড করা
app.secret_key = "supersecret123"

# BUG 5: কুকির সিকিউরিটি ফ্ল্যাগ বন্ধ
app.config.update(
    SESSION_COOKIE_HTTPONLY=False,
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_SAMESITE=None,
)

# BUG 6: যেকোনো origin থেকে credentials সহ রিকোয়েস্ট অনুমোদিত
CORS(app, origins="*", supports_credentials=True)

# BONUS: প্লেইনটেক্সট পাসওয়ার্ড কোডে
USERS = {
    "alice": {"password": "alice123", "role": "user"},
    "admin": {"password": "admin123", "role": "admin"},
}


@app.route("/")
def index():
    return jsonify(
        app="Vulnerable Flask Lab",
        endpoints=["/login", "/calc?expr=2+2", "/run", "/admin", "/api/profile", "/boom"],
    )


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    user = USERS.get(data.get("username"))
    if user and user["password"] == data.get("password"):
        session["user"] = data["username"]
        session["role"] = user["role"]
        return jsonify(status="ok")
    return jsonify(status="fail"), 401


@app.route("/calc")
def calc():
    expr = request.args.get("expr", "")
    try:
        result = eval(expr)  # BUG 1
    except Exception as e:
        result = f"error: {e}"  # BONUS: ভেতরের তথ্য লিক
    return jsonify(expr=expr, result=str(result))


@app.route("/run", methods=["POST"])
def run():
    code = (request.get_json(silent=True) or {}).get("code", "")
    scope = {}
    exec(code, scope)  # BUG 2
    return jsonify(result=str(scope.get("result")))


@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return jsonify(error="forbidden"), 403
    return jsonify(secret_report="Q4 financials: CONFIDENTIAL")


@app.route("/api/profile")
def profile():
    if "user" not in session:
        return jsonify(error="login required"), 401
    return jsonify(user=session["user"], role=session["role"], email=f"{session['user']}@lab.local")


@app.route("/boom")
def boom():
    return 1 / 0  # ইচ্ছাকৃত exception — debugger দেখানোর জন্য


if __name__ == "__main__":
    # BUG 3: debug=True + সব ইন্টারফেসে বাইন্ড
    app.run(host="0.0.0.0", port=5000, debug=True)
