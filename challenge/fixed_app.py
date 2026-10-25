# ইন্সট্রাক্টর সমাধান: শিক্ষার্থীদের আগে দেখাবেন না
import re
import subprocess
from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)
HOST_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.-]{0,252}$")

@app.route("/ping")
def ping():
    host = request.args.get("host", "")
    if not HOST_RE.match(host):
        return "Bad Request: Invalid host", 400
    out = subprocess.run(["ping", "-c", "1", host], capture_output=True, text=True, timeout=5)
    return out.stdout

@app.route("/hello")
def hello():
    name = request.args.get("name", "")
    return f"Hello {escape(name)}"
