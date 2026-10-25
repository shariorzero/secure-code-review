"""
ল্যাবের ফাইল: student/app.py
  ল্যাব ক: প্রতিটি `# RED FLAG` মার্কারের পাশে ৩টি প্রশ্নের উত্তর লিখুন
            (ইনপুট কোথা থেকে? বিপজ্জনক জায়গা কোনটি? মাঝখানে পাহারা আছে কি?)
  ল্যাব খ: `# TODO` অনুযায়ী ঠিক করুন, তারপর একই curl কমান্ড আবার চালিয়ে যাচাই করুন।
⚠️ ইচ্ছাকৃতভাবে দুর্বল। শুধু লোকাল/Codespaces-এ চালান।
"""
import ast
import operator
import os  # RED FLAG 3 ঠিক করতে লাগবে

from flask import Flask, request, jsonify, session
from flask_cors import CORS

# ---- সাহায্যকারী: ল্যাব খ-এ eval-এর বদলে এটি ব্যবহার করবেন ----
# শুধু সংখ্যা ও + - * / বোঝে, বাকি সবকিছুতে ValueError দেয়।
_OPS = {ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv}


def safe_eval(expr):
    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and type(n.value) in (int, float):
            return n.value
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
            return -ev(n.operand)
        if isinstance(n, ast.BinOp) and type(n.op) in _OPS:
            return _OPS[type(n.op)](ev(n.left), ev(n.right))
        raise ValueError("not allowed")
    return ev(ast.parse(expr, mode="eval"))


# ---- অ্যাপ শুরু ----
app = Flask(__name__)

# RED FLAG 3: secret_key | ইনপুট: ____ | বিপজ্জনক জায়গা: ____ | পাহারা: ____
# TODO (ল্যাব খ): চাবি কোডের বাইরে রাখুন
app.secret_key = "supersecret123"

# RED FLAG 4: কুকির ফ্ল্যাগ | তিনটির কোনটি বন্ধ? ঝুঁকি কী? ____
# TODO (ল্যাব খ, বোনাস): তিনটি ফ্ল্যাগ চালু করুন, SAMESITE="Lax"
app.config.update(
    SESSION_COOKIE_HTTPONLY=False,
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_SAMESITE=None,
)

# RED FLAG 5: CORS | কাদের ঢুকতে দেওয়া হচ্ছে? কাদের দেওয়া উচিত? ____
# TODO (ল্যাব খ, বোনাস): নির্দিষ্ট origin-এর তালিকা দিন
CORS(app, origins="*", supports_credentials=True)

# BONUS FLAG: কোডে লেখা পাসওয়ার্ড | কেন সমস্যা? ____
USERS = {
    "alice": {"password": "alice123", "role": "user"},
    "admin": {"password": "admin123", "role": "admin"},
}


@app.route("/")
def index():
    return jsonify(
        app="Student Flask Lab",
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
        # RED FLAG 1a: eval( | ইনপুট: ____ | বিপজ্জনক জায়গা: ____ | পাহারা: ____
        # TODO (ল্যাব খ): eval বদলে safe_eval ব্যবহার করুন
        result = eval(expr)
    except Exception as e:
        # BONUS FLAG: ভেতরের তথ্য ইউজারকে ফেরত যাচ্ছে | কেন সমস্যা? ____
        result = f"error: {e}"
    return jsonify(expr=expr, result=str(result))


# RED FLAG 1b: exec( | ইনপুট: ____ | বিপজ্জনক জায়গা: ____ | পাহারা: ____
# TODO (ল্যাব খ): ইউজার কেন নিজের কোড পাঠাবে? রুটটি কি আদৌ দরকার?
@app.route("/run", methods=["POST"])
def run():
    code = (request.get_json(silent=True) or {}).get("code", "")
    scope = {}
    exec(code, scope)
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
    return 1 / 0  # ইচ্ছাকৃত exception, debugger দেখার জন্য


if __name__ == "__main__":
    # RED FLAG 2: debug মোড | কোথায় চালালে বিপদ? ____
    # TODO (ল্যাব খ): debug বাদ দিন, host কেবল নিজের মেশিনে রাখুন
    app.run(host="0.0.0.0", port=5000, debug=True)
