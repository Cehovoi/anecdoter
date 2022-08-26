from flask import render_template, redirect, request, url_for
from flask_login import login_user, logout_user, current_user
from ane_searcher_bot import db
from .blue_app import blue
from .consts import GRADE
from .models import User, RatedJokes

@blue.route('/newspaper')
def newspaper():
    jokes = db.session.query(RatedJokes).all()
    return render_template('index.html',
                           rating=0,
                           jokes=[(joke.joke, joke.position,
                                   joke.grade * GRADE) for joke in jokes])


@blue.route('/rating/<int:num>')
def index(num):
    jokes = db.session.query(RatedJokes).filter_by(
        grade=num).order_by(RatedJokes.position)
    #jokes = db.session.query(RatedJokes).order_by(RatedJokes.grade).paginate(num, 9, False)

    stars = GRADE * num

    return render_template('index.html',
                           rating=num,
                           stars=stars,
                           jokes=[(joke.joke, joke.position) for joke in jokes])


@blue.route('/create_db')
def create_db():
    db.create_all()
    return 'db.create_all()'


@blue.route('/login', methods=['POST', 'GET'])
def login():
    print("@app.route('/login', methods=['POST', 'GET'])\n")
    print("request.method", request.method)
    if request.method == 'POST':
        admin = db.session.query(User).filter(User.username == request.form['username']).first()
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