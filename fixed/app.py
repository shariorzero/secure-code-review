"""
✅ Fixed version — Class 1 Flask Lab
প্রতিটি পরিবর্তনের পাশে FIX 1..6 কমেন্ট আছে।
চালানোর আগে .env.example দেখুন (SECRET_KEY, ADMIN_PASSWORD, ALICE_PASSWORD লাগবে)।
"""
import ast
import operator
import os

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# FIX 4: সিক্রেট এনভায়রনমেন্ট থেকে; না থাকলে অ্যাপ চালুই হবে না (fail fast)
app.secret_key = os.environ["SECRET_KEY"]

# FIX 5: কুকি হার্ডেনিং
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "1") == "1",
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=1800,
)

# FIX 6: শুধু অনুমোদিত origin
ALLOWED_ORIGINS = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")]
CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=True)

# BONUS FIX: পাসওয়ার্ড হ্যাশ করে রাখা (বাস্তবে ডাটাবেস থাকবে)
USERS = {
    "alice": {"hash": generate_password_hash(os.environ["ALICE_PASSWORD"]), "role": "user"},
    "admin": {"hash": generate_password_hash(os.environ["ADMIN_PASSWORD"]), "role": "admin"},
}

# FIX 1: eval() বাদ। AST দিয়ে শুধু সংখ্যা ও + - * / অনুমোদিত (** ইচ্ছাকৃতভাবে বাদ: DoS ঝুঁকি)
_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def safe_eval(expr: str):
    if len(expr) > 100:
        raise ValueError("expression too long")

    def _ev(node):
        if isinstance(node, ast.Expression):
            return _ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](_ev(node.left), _ev(node.right))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -_ev(node.operand)
        raise ValueError("unsupported expression")

    return _ev(ast.parse(expr, mode="eval"))


# FIX 2: exec() বাদ। ইউজারের কোড নয়, শুধু নামকরা allowlist অপারেশন
ALLOWED_OPS = {"upper": str.upper, "lower": str.lower, "reverse": lambda s: s[::-1]}


@app.route("/")
def index():
    return jsonify(app="Fixed Flask Lab", endpoints=["/login", "/calc?expr=2+2", "/run", "/admin", "/api/profile"])


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    user = USERS.get(data.get("username"))
    if user and check_password_hash(user["hash"], str(data.get("password", ""))):
        session.clear()
        session["user"] = data["username"]
        session["role"] = user["role"]
        return jsonify(status="ok")
    return jsonify(status="fail"), 401


@app.route("/calc")
def calc():
    expr = request.args.get("expr", "")
    try:
        result = safe_eval(expr)
    except (ValueError, SyntaxError, ZeroDivisionError):
        return jsonify(error="invalid expression"), 400  # ভেতরের তথ্য লিক নয়
    return jsonify(expr=expr, result=str(result))


@app.route("/run", methods=["POST"])
def run():
    data = request.get_json(silent=True) or {}
    op = ALLOWED_OPS.get(data.get("op"))
    text = data.get("text")
    if op is None or not isinstance(text, str) or len(text) > 1000:
        return jsonify(error="invalid request"), 400
    return jsonify(result=op(text))


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
    return 1 / 0


@app.errorhandler(Exception)
def handle_error(e):
    if isinstance(e, HTTPException):
        return jsonify(error=e.name), e.code
    app.logger.exception("unhandled error")  # লগে থাকবে, ইউজারকে নয়
    return jsonify(error="internal server error"), 500


if __name__ == "__main__":
    # FIX 3: debug নেই, শুধু লোকালহোস্টে। প্রোডাকশনে gunicorn/uwsgi ব্যবহার করুন
    app.run(host="127.0.0.1", port=5000)
