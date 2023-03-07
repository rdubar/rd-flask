import sqlite3, os
from flask import Flask, render_template, request, url_for, flash, redirect

from flask_bootstrap import Bootstrap4
from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = PLEX_TOKEN = os.environ.get('SECRET KEY', 'WARNING! SET A SECRET KEY!')

bootstrap = Bootstrap4(app)

from routes import *
app.register_blueprint(routes)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)