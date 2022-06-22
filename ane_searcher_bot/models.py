from datetime import datetime

from sqlalchemy import create_engine, Integer, Column, String, ForeignKey, \
    DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

engine = create_engine(
    "postgresql://zhenya:123@localhost/test_tg",
    execution_options={
        "isolation_level": "REPEATABLE READ"
    }
)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    words = relationship('Word')
    state = Column(String, default='start')
    created = Column(DateTime, default=datetime.now())

    def __init__(self, chat_id, words):
        self.chat_id = chat_id
        self.words = words

    def __repr__(self):
        return f'<User - {self.chat_id}, ' \
               f'created - {self.created}, ' \
               f'words - {self.words}>'


class Word(Base):
    __tablename__ = 'words'
    id = Column(Integer, primary_key=True)
    word = Column(String(128))
    amount_pages = Column(Integer)
    joke_index = Column(Integer, default=1)
    page_num = Column(Integer, default=1)
    chat_id = Column(Integer, ForeignKey("users.chat_id"))
    created = Column(DateTime, default=datetime.now)

    def __init__(self, word, amount_pages):
        self.word = word
        self.amount_pages = amount_pages

    def __repr__(self):
        return f'<Word - {self.word}, ' \
               f'joke_index - {self.joke_index}, ' \
               f'page_num - {self.page_num}, ' \
               f'amount_pages - {self.amount_pages}, ' \
               f'created - {self.created}'


def recreate_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
session = Session()


if __name__ == '__main__':
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    session = Session()
    #Base.query = session.query_property()

    # recreate_database()
    #Base.metadata.create_all(engine)
    user = session.query(User).filter_by(chat_id=540439923).first()
    print(user)
    word = session.query(Word).filter_by(word='говно').first()
    print(word)
    # word.joke_index = 5
    # word.page_num=2
    # session.add(word)
    # session.commit()
    # session.close()



    # user = session.query(User).filter(User.words.any(word='говно')).filter(User(chat_id=540439923)).all()
    #user = session.query(User).filter(User.words.any(word='говно'), User(chat_id=540439923))
    #user.filter_by(chat_id=540439923).all()
    # user = session.query(User).filter_by(chat_id=540439923)
    # print("user first", user.first())
    # print("dsada", user.filter(User.words.any(word='говно')).first())




    # word = Word('ципа', amount_pages=5)
    # session.add(word)
    # zhenya = User('567', [word])
    # session.add(zhenya)
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