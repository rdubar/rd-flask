from flask import render_template
from . import routes

@routes.route('/users')
def users():
    return "USERS"
    return render_template('users.html')