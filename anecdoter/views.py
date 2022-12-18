from flask import render_template, redirect, request, url_for
from flask_login import login_user, logout_user, current_user
from sqlalchemy.exc import IntegrityError

from anecdoter.web_app import db
from .blue_app import blue
from .consts import GRADE, AMOUNT_JOKES_FOR_RATING, LOGIN_ERROR
from .models import User, RatedJokes


@blue.route('/rating/<int:page>/<int:user_id>')
def rating(page, user_id):
    jokes = db.session.query(RatedJokes).order_by(
        RatedJokes.grade).paginate(page, AMOUNT_JOKES_FOR_RATING, False)
    stars = GRADE * page
    jokes.items.sort(key=lambda x: getattr(x, 'position'))
    return render_template('index.html',
                           id=user_id,
                           stars=stars,
                           jokes=jokes)


@blue.route('/login/<int:user_id>', methods=['POST', 'GET'])
def login(user_id):
    print("login(user_id):\n"*10)
    if request.method == 'POST':
        login = request.form.get('login', None)
        password = request.form.get('password', None)
        reg_button = request.form.get('REG', None)
        print('password login', password, login)
        if reg_button:
            print("reg_button")
            user = db.session.query(User).filter_by(user_id=user_id,
                                                    role='admin').first()
            user.login = login
            user.set_password = password
            try:
                db.session.add(user)
                db.session.commit()

            except IntegrityError:
                return render_template('fail.html',
                                       id=user_id,
                                       message='USERNAME ALREADY TAKEN')
            login_user(user)
            db.session.close()
            return redirect(url_for('admin.index'))

        user = db.session.query(User).filter_by(login=login,
                                                role='admin').first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin.index'))
        else:
            return render_template('fail.html',
                                   id=user_id,
                                   message='WRONG LOGIN OR PASSWORD')
    user = db.session.query(User).filter_by(user_id=user_id).first()
    if not user:
        return render_template('fail.html',
                               id=user_id,
                               message=LOGIN_ERROR)
    if user.login:
        button = 'LOGIN'
    else:
        button = 'REG'
    return render_template('login.html', id=user_id, button=button)


@blue.route('/logout')
def logout():
    user_id = current_user.user_id
    logout_user()
    return redirect(f'/rating/1/{user_id}')


