from functools import wraps
from flask import request, redirect, url_for, session

import cloudinary
import cloudinary.uploader
import cloudinary.api

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(session.get('email'))
        if session.get("email") is None:
            return redirect("/analysis/authorize")
        return f(*args, **kwargs)
    return decorated_function

cloudinary.config(
    cloud_name = "boyuan12",
    api_key = "893778436618783",
    api_secret = "X4LufXPHxvv4hROS3VZWYyR3tIE"
)

def upload_image(file):
    r = cloudinary.uploader.upload(file)
    img_url = r["secure_url"]
    return img_url
