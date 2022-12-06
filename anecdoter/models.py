from datetime import datetime
from flask_login import UserMixin, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin.contrib.sqla import ModelView
from anecdoter.web_app import db, admin, login


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # todo need overrite chat_id(int) to user_id(str)
    #user_id = db.Column(db.String(64), unique=True)
    chat_id = db.Column(db.Integer, unique=True)
    words = db.relationship('Word')
    # TODO add login field, remove unique from username
    #username = db.Column(db.String(64), nullable=True,)
    role = db.Column(db.String(64), default='user')
    #login = db.Column(db.String(64), nullable=True, unique=True)
    password_hash = db.Column(db.String(512), nullable=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)
    # TODO add already_rated list field bind with RatedJokes.message_id field

    def __init__(self, chat_id):
        self.chat_id = chat_id

    @property
    def set_password(self):
        raise AttributeError('set_password is not readable attribute')

    @set_password.setter
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'\nchat_id == {self.chat_id}\n' \
               f'username == {self.username}\n' \
               f'created_on == {self.created_on}\n' \
               f'role == {self.role}\n\n' \
               f'{"w_"*20}\nwords == {self.words}\n{"w_"*20}\n'


class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(128))
    amount_pages = db.Column(db.Integer)
    joke_index = db.Column(db.Integer, default=1)
    page_num = db.Column(db.Integer, default=1)
    chat_id = db.Column(db.Integer, db.ForeignKey("users.chat_id"))
    created = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, word, amount_pages, chat_id):
        self.word = word
        self.amount_pages = amount_pages
        self.chat_id = chat_id

    def __repr__(self):
        return f'\nword == {self.word}\n' \
               f'joke_index == {self.joke_index}\n' \
               f'page_num == {self.page_num}\n' \
               f'amount_pages == {self.amount_pages}\n' \
               f'created == {self.created}\n'


class RatedJokes(db.Model):
    __tablename__ = 'rated_jokes'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(128))
    joke = db.Column(db.Text(), nullable=False)
    grade = db.Column(db.Integer, default=1)
    position = db.Column(db.Integer, default=1)
    # todo add chat_id field bind with chat_id many(chat_id) -> one(user)
    # before add new RatedJokes check words for coordinate fields
    # if several rated (several chat_id) grade several numbers

    def __init__(self, joke, grade, word):
        self.word = word
        self.joke = joke
        self.grade = grade

    def __repr__(self):
        return f'\nword == {self.word}\n' \
               f'joke == {self.joke}\n'\
               f'grade == {self.grade}\n' \
               f'position == {self.position}\n'


@login.user_loader
def load_user(id):
    return db.session.query(User).get(id)


class MyModelView(ModelView):
    """
        Flask Admin settings
    """
    column_exclude_list = ['password_hash', ]
    column_searchable_list = ['chat_id']

    def is_accessible(self):
        if current_user.role != 'admin':
            MyModelView.can_create = False
            MyModelView.can_edit = False
            MyModelView.can_delete = False
        return current_user.is_authenticated


admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Word, db.session))


def recreate_database():
    db.drop_all()
    db.create_all()
