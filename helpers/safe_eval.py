"""ল্যাব খ-এর জন্য: এই ফাংশনটি student/app.py-র ওপরে বসান, তারপর eval(expr) বদলে safe_eval(expr) লিখুন।
শুধু সংখ্যা ও + - * / বোঝে, বাকি সবকিছুতে ValueError।"""
import ast, operator, os

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv}

def safe_eval(expr):
    def ev(n):
        if isinstance(n, ast.Expression): return ev(n.body)
        if isinstance(n, ast.Constant) and type(n.value) in (int, float): return n.value
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub): return -ev(n.operand)
        if isinstance(n, ast.BinOp) and type(n.op) in _OPS:
            return _OPS[type(n.op)](ev(n.left), ev(n.right))
        raise ValueError("not allowed")
    return ev(ast.parse(expr, mode="eval"))
