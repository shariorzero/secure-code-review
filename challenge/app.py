from flask import Flask, request
import os

app = Flask(__name__)

@app.route("/ping")
def ping():
    host = request.args.get("host", "")
    return os.popen("ping -c 1 " + host).read()

@app.route("/hello")
def hello():
    name = request.args.get("name", "")
    return f"Hello {name}"
