from flask import render_template, redirect, request, url_for
from flask_login import login_user, logout_user, current_user
from app import app
from ane_searcher_bot import db
from ane_searcher_bot.models import Owner
from .blue_app import blue


@blue.route('/')
def check():
    return 'FLASK WORKING'


@blue.route('/create_db')
def create_db():
    db.create_all()
    return 'db.create_all()'


@blue.route('/login', methods=['POST', 'GET'])
def login():
    print("@app.route('/login', methods=['POST', 'GET'])\n"*5)
    print("request.method", request.method)
    if request.method == 'POST':
        admin = db.session.query(Owner).filter(Owner.username == request.form['username']).first()
        if admin and admin.check_password(request.form['password']):
            login_user(admin)
            return redirect(url_for('admin.index'))
        else:
            return render_template('fail.html')
    return render_template('login.html')

@blue.route('/logout')
def logout():
    logout_user()
    return redirect('/start')