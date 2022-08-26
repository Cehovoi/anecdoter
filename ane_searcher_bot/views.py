from flask import render_template, redirect, request, url_for
from flask_login import login_user, logout_user, current_user
from sqlalchemy.exc import IntegrityError

from ane_searcher_bot import db
from .blue_app import blue
from .consts import GRADE, AMOUNT_JOKES_FOR_RATING
from .models import User, RatedJokes


@blue.route('/rating/<int:page>/<int:chat_id>')
def rating(page, chat_id):
    jokes = db.session.query(RatedJokes).order_by(
        RatedJokes.grade).paginate(page, AMOUNT_JOKES_FOR_RATING, False)
    stars = GRADE * page
    jokes.items.sort(key=lambda x: getattr(x, 'position'))
    return render_template('index.html',
                           id=chat_id,
                           stars=stars,
                           jokes=jokes)


@blue.route('/create_db')
def create_db():
    db.create_all()
    return 'db.create_all()'


@blue.route('/login/<int:chat_id>', methods=['POST', 'GET'])
def login(chat_id):
    print("@app.route('/login', methods=['POST', 'GET'])\n")
    print("request.method", request.method)

    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        reg_button = request.form.get('reg', None)
        user = db.session.query(User).filter_by(username=username,
                                                chat_id=chat_id).first()
        if not user and reg_button:
            print("chat_id", chat_id)
            user = db.session.query(User).filter_by(chat_id=chat_id).first()
            if not user:
                # to fail.html
                print("СХОДИКА в ТЕЛЕГРАМ")
            user.username = username
            user.set_password = password
            try:
                db.session.add(user)
                db.session.commit()
                db.session.close()
            except IntegrityError as e:
                return render_template('fail.html',
                                       id=chat_id,
                                       message='USERNAME ALREADY TAKEN')
            login_user(user)
            return redirect(url_for('admin.index'))

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin.index'))
        else:
            print('before fail\n'*10)
            return render_template('fail.html',
                                   id=chat_id,
                                   message='WRONG PASSWORD')
    return render_template('login.html', id=chat_id)

@blue.route('/logout')
def logout():
    chat_id = current_user.chat_id
    logout_user()
    return redirect(f'/rating/1/{chat_id}')
