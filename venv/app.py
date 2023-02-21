import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect

from flask_bootstrap import Bootstrap4
from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'D9oassl9.AxbLkOkY91VYhr#e`W3[m}cpJZ?qcD&=Nzs,^J33D]C>;l&MHdc-Sz'

bootstrap = Bootstrap4(app)

from routes import *
app.register_blueprint(routes)


