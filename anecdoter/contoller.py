from os import getenv
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import load_only
from anecdoter.models import Word, User, RatedJokes
from anecdoter.consts import AMOUNT_JOKES_FOR_RATING

from anecdoter.parser import get_jokes


def db_connector():
    database_url = getenv('DATABASE_URL')
    database_url = 'postgresql://zhenya:123@localhost/anecdoter_db'
    engine = create_engine(
        database_url,
        execution_options={
            "isolation_level": "REPEATABLE READ"
        }
    )
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    session = Session()
    return session


class Combiner:
    def __init__(self, uid, word, amount_pages=0,
                 joke_index=0, page_num=1, jokes_len=0):
        self.uid = uid
        self.word = word
        self.amount_pages = amount_pages
        self.joke_index = joke_index
        self.page_num = page_num
        self.jokes_len = jokes_len

    def run_parser(self):
        jokes, amount_pages = get_jokes(self.word, self.page_num,
                                        self.amount_pages)
        self.amount_pages = amount_pages
        self.jokes_len = len(jokes)
        # new attribute, with jokes list
        self.jokes = jokes[self.joke_index:]

    def sync_db(self, change_word=False):
        from anecdoter import create_app
        create_app().app_context().push()
        from anecdoter import db
        from .models import User, Word
        word = db.session.query(Word).filter_by(chat_id=self.uid,
                                                word=self.word).first()
        if change_word:
            # user want another theme, save current theme for parser to db
            page_num, joke_index, amount_pages = \
                self.page_num, self.joke_index, self.amount_pages
            if page_num <= amount_pages:
                if self.jokes_len > joke_index:
                    joke_index += 1
                else:
                    if page_num == amount_pages:
                        page_num = 1
                        joke_index = 0
                    else:
                        page_num += 1
                        joke_index = 0

            word.page_num = page_num
            word.joke_index = joke_index
            word.amount_pages = amount_pages
            self.save([word], db)

        else:
            if word:
                # read info for parser from db
                self.page_num = word.page_num
                self.joke_index = word.joke_index
                self.amount_pages = word.amount_pages
                self.run_parser()
            else:
                # create db record
                self.run_parser()
                # jokes does not exists
                if not self.amount_pages:
                    return
                word = Word(word=self.word, amount_pages=self.amount_pages,
                            chat_id=self.uid)
                user = db.session.query(User).filter_by(chat_id=self.uid).first()
                if user:
                    self.save([word], db)
                    return
                user = User(chat_id=self.uid)
                self.save([word, user], db)

    @staticmethod
    def save(obj, db):
        db.session.add_all(obj)
        db.session.commit()
        db.session.close()

    @lru_cache
    def jokefunc(self):
        for joke in self.jokes:
            yield joke.text


class RatingFill:

    def __init__(self, word, joke, grade):
        self.word = word
        self.joke = joke
        self.grade = grade

    def update_db(self):
        from anecdoter import create_app
        create_app().app_context().push()
        from anecdoter import db
        from .models import RatedJokes
        jokes = db.session.query(RatedJokes).filter_by(
            grade=self.grade).options(load_only(RatedJokes.position))
        stack_jokes = []
        for joke in jokes:
            joke.position += 1
            if joke.position >= AMOUNT_JOKES_FOR_RATING+1:
                self.delete(joke, db)
                continue
            stack_jokes.append(joke)

        joke = RatedJokes(word=self.word, joke=self.joke, grade=self.grade)
        stack_jokes.append(joke)
        self.save(stack_jokes, db)

    @staticmethod
    def save(obj, db):
        db.session.add_all(obj)
        db.session.commit()
        db.session.close()

    @staticmethod
    def delete(obj, db):
        db.session.delete(obj)
        db.session.commit()


if __name__ == '__main__':

    session = db_connector()
    words = session.query(Word).all()
    print(words)


