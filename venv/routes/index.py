from flask import render_template
from . import routes

import secrets
import string

def generate_password(length=20, safe=False):
    if safe:
        return secrets.token_urlsafe(length)
    else:
        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        return password

def random_case(text):
    return ''.join(choice((str.upper, str.lower))(c) for c in text)

@routes.route('/')
def index():
    return render_template('index.html', password=generate_password(safe=True))