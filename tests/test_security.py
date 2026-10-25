"""
ব্যবহার:
  TARGET=vulnerable pytest -q   # ব্যর্থ হওয়াই প্রত্যাশিত (বাগ প্রমাণ)
  TARGET=student pytest -q      # শিক্ষার্থীর নিজের প্যাচ যাচাই
  TARGET=fixed pytest -q        # সব পাস হবে
AI-এর দেওয়া fix যাচাই করতেও এই টেস্ট ব্যবহার করুন।
"""
import importlib.util
import os
import pathlib

import pytest
from flask import Flask
from flask.sessions import SecureCookieSessionInterface

TARGET = os.environ.get("TARGET", "fixed")
ROOT = pathlib.Path(__file__).resolve().parent.parent
APP_FILE = ROOT / TARGET / "app.py"

os.environ.setdefault("SECRET_KEY", "test-only-secret-not-the-lab-one")
os.environ.setdefault("ADMIN_PASSWORD", "test-admin-pw")
os.environ.setdefault("ALICE_PASSWORD", "test-alice-pw")
os.environ["COOKIE_SECURE"] = "1"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("target_app", APP_FILE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture()
def client(mod):
    mod.app.config["TESTING"] = True
    return mod.app.test_client()


def alice_password():
    return os.environ["ALICE_PASSWORD"] if TARGET == "fixed" else "alice123"


def test_eval_rce_blocked(client):
    r = client.get("/calc", query_string={"expr": "__import__('os').getcwd()"})
    assert os.getcwd() not in r.get_data(as_text=True)


def test_calc_still_works(client):
    r = client.get("/calc", query_string={"expr": "2*(3+4)"})
    assert r.status_code == 200 and r.get_json()["result"] == "14"


def test_exec_blocked(client):
    r = client.post("/run", json={"code": "result = 40 + 2"})
    assert "42" not in r.get_data(as_text=True)


def test_debug_not_enabled():
    assert "debug=True" not in APP_FILE.read_text()


def test_cookie_flags(client):
    r = client.post("/login", json={"username": "alice", "password": alice_password()})
    cookie = r.headers.get("Set-Cookie", "")
    assert "HttpOnly" in cookie
    assert "Secure" in cookie
    assert "SameSite" in cookie


def test_cors_not_open(client):
    r = client.get("/", headers={"Origin": "https://evil.example"})
    allow = r.headers.get("Access-Control-Allow-Origin")
    assert allow not in ("*", "https://evil.example")


def test_forged_admin_cookie_rejected(client):
    fake = Flask("fake")
    fake.secret_key = "supersecret123"
    forged = SecureCookieSessionInterface().get_signing_serializer(fake).dumps({"user": "admin", "role": "admin"})
    client.set_cookie("session", forged)
    assert client.get("/admin").status_code == 403
