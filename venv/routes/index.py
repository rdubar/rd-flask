from flask import render_template, request
from . import routes

import secrets
import string


def generate_password(length=20, safe=False):
    if safe:
        password =''
        while (not '_' in password) and (not '-' in password):
            password = secrets.token_urlsafe(length)
        return password
    else:
        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        return password

def random_case(text):
    return ''.join(secrets.choice((str.upper, str.lower))(c) for c in text)

@routes.route('/')
def index():
    return render_template('index.html', password=generate_password(safe=True))

@routes.route('/randomcase/', methods=('GET', 'POST'))
def randomcase():
    text = ''
    if request.method == 'POST':
        text = request.form['text']
    if text == '':
        text = 'random text'
    return render_template('former.html', text = random_case(text), title=random_case('randomcase'))