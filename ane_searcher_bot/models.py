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
    chat_id = Column(Integer)
    words = relationship('Word')
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
    joke_index = Column(Integer, default=1)
    page_num = Column(Integer, default=1)
    amount_pages = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
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

if __name__ == '__main__':
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    session = Session()
    #recreate_database()
    #Base.metadata.create_all(engine)



    # word = Word('ципа', amount_pages=5)
    # session.add(word)
    # zhenya = User('567', [word])
    # session.add(zhenya)
    # print("session.new", session.new)
    # session.commit()
    # session.close()
    #
    w = session.query(Word).all()
    u = session.query(User).all()
    print('w', w,  '\nu', u)

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