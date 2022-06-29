from functools import wraps
from flask import request, redirect, url_for, session

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(session.get('email'))
        if session.get("email") is None:
            return redirect("/analysis/authorize")
        return f(*args, **kwargs)
    return decorated_function
