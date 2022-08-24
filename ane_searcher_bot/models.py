from datetime import datetime
from flask_login import UserMixin, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin.contrib.sqla import ModelView
from ane_searcher_bot import db, admin, login


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, unique=True)
    words = db.relationship('Word')
    username = db.Column(db.String(64), nullable=True, unique=True)
    password = db.Column(db.String(64), nullable=True)
    password_hash = db.Column(db.String(512), nullable=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

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
        return f'\nchat_id = {self.chat_id}\n' \
               f'username = {self.username}\n' \
               f'created_on = {self.created_on}\n' \
               f'words = {self.words}\n'


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
        return f'<Word - {self.word}, ' \
               f'joke_index - {self.joke_index}, ' \
               f'page_num - {self.page_num}, ' \
               f'amount_pages - {self.amount_pages}, ' \
               f'created - {self.created}'


@login.user_loader
def load_user(id):
    return db.session.query(User).get(id)  # Owner.query.get(id)


class MyModelView(ModelView):
    can_delete = True

    def is_accessible(self):
        return current_user.is_authenticated


admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Word, db.session))


def recreate_database():
    # Base.metadata.drop_all(engine)
    # Base.metadata.create_all(engine)
    db.drop_all()
    db.create_all()





if __name__ == '__main__':
    from sqlalchemy import create_engine
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, relationship
    # engine = create_engine(
    #     "postgresql://zhenya:123@localhost/test_tg",
    #     execution_options={
    #         "isolation_level": "REPEATABLE READ"
    #     }
    # )
    engine = create_engine(
        'postgresql://zhenyavo:dun5k466@localhost/jokes_peeper',
        execution_options={
            "isolation_level": "REPEATABLE READ"
        }
    )

    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    session = Session()

    # Base.query = session.query_property()
    # db.create_all()
    #recreate_database()
    # Base.metadata.create_all(engine)

    chat_id_1 = 540439923
    chat_id_2 = 123
    chat_id_3 = 321
    # user = session.query(User).filter_by(chat_id=chat_id_2).first()
    # print(user)
    user = session.query(User).all()
    print(user)
    word = session.query(Word).filter_by(word='говно', chat_id=chat_id_1).first()
    print(word)
    # session.delete(word)
    # session.commit()
    # print("word", word)
    #
    #
    # word = session.query(Word).filter_by(word='говно', chat_id=chat_id_2).first()
    # print(word)
    # word.page_num = 1
    # word.joke_index = 11
    # session.add(word)
    # session.commit()
    # session.close()
    # session.delete(word)
    # session.commit()
    # session.close()

    # word.joke_index = 5
    # word.page_num=2
    # session.add(word)
    # session.commit()
    # session.close()

    # user = session.query(User).filter(User.words.any(word='говно')).filter(User(chat_id=540439923)).all()
    # user = session.query(User).filter(User.words.any(word='говно'), User(chat_id=540439923))
    # user.filter_by(chat_id=540439923).all()
    # user = session.query(User).filter_by(chat_id=540439923)
    # print("user first", user.first())
    # print("dsada", user.filter(User.words.any(word='говно')).first())

    # word = Word(chat_id='999', word='ципа', amount_pages=5)
    # user = User(chat_id='999')
    # obj = [word, user]
    # session.add_all(obj)
    # print("session.new", session.new)
    # session.commit()
    # session.close()
    #
    # w = session.query(Word).all()
    # u = session.query(User).all()
    # print('w', w,  '\nu', u)

    # u = session.query(User).filter_by(chat_id='567').first()
    # word2 = Word('пипа', 1, 1, 5)
    # u.word.append(word2)
    # print("u", u)
    # print("session.new", session.new)
    # session.commit()
    # session.close()

    # u = session.query(User).filter_by(chat_id='567').first()
    # print('u', u)
    # w = session.query(Word).filter_by(word='пипа').first()
