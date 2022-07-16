from flask import render_template
from . import auth

@auth.route('/login')
def login():
    print("@auth.route('/login')\n"*5)
    return render_template('login.html')