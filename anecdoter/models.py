from datetime import datetime
from flask_login import UserMixin, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin.contrib.sqla import ModelView
from anecdoter.web_app import db, admin, login


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True)
    words = db.relationship('Word', cascade='all, delete', backref='parent')
    rated = db.relationship('RatedJokes', cascade='all, delete',
                            backref='parent')
    username = db.Column(db.String(64), nullable=True,)
    role = db.Column(db.String(64), default='user')
    login = db.Column(db.String(64), nullable=True, unique=True)
    password_hash = db.Column(db.String(512), nullable=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username

    @property
    def set_password(self):
        raise AttributeError('set_password is not readable attribute')

    @set_password.setter
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'user_id== {self.user_id};' \
               f'username == {self.username};' \
               f'created_on == {self.created_on};' \
               f'role == {self.role};' \
               f'words == {self.words};'


class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(128))
    amount_pages = db.Column(db.Integer)
    joke_index = db.Column(db.Integer, default=1)
    page_num = db.Column(db.Integer, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    created = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, word, amount_pages, user_id):
        self.word = word
        self.amount_pages = amount_pages
        self.user_id = user_id

    def __repr__(self):
        return f'word == {self.word};' \
               f'joke_index == {self.joke_index};' \
               f'page_num == {self.page_num};' \
               f'amount_pages == {self.amount_pages};' \
               f'created == {self.created};'


class RatedJokes(db.Model):
    __tablename__ = 'rated_jokes'
    id = db.Column(db.Integer, primary_key=True)
    joke = db.Column(db.Text(), nullable=False)
    grade = db.Column(db.Integer, default=1)
    position = db.Column(db.Integer, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __init__(self, user_id, joke, grade):
        self.user_id = user_id
        self.joke = joke
        self.grade = grade

    def __repr__(self):
        return f'user_id == {self.user_id};' \
               f'joke == {self.joke};'\
               f'grade == {self.grade};' \
               f'position == {self.position};'


@login.user_loader
def load_user(id):
    return db.session.query(User).get(id)


class MyModelView(ModelView):
    """
        Flask Admin settings
    """
    column_exclude_list = ['password_hash', ]
    column_searchable_list = ['user_id']

    def is_accessible(self):
        if hasattr(current_user, 'role') and current_user.role != 'admin':
            MyModelView.can_create = False
            MyModelView.can_edit = False
            MyModelView.can_delete = False
        return current_user.is_authenticated


admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Word, db.session))
admin.add_view(MyModelView(RatedJokes, db.session))


def recreate_database():
    db.drop_all()
    db.create_all()
