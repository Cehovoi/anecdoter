from functools import lru_cache

from ane_searcher_bot.parser import get_jokes
from .models import User, Word, session


class Combiner:
    def __init__(self, uid, word, amount_pages=None,
                 joke_index=0, page_num=1, state='start', jokes=[]):
        self.uid = uid
        self.word = word
        self.amount_pages = amount_pages
        self.joke_index = joke_index
        self.page_num = page_num
        self.state = state
        self.jokes = jokes

    def run_parser(self):
        jokes, amount_pages = get_jokes(self.word, self.page_num) # добавить номер страницы
        self.jokes = jokes[self.joke_index:] # добавить индекс сюда
        self.amount_pages = amount_pages

    def create_user(self):
        word = Word(word=self.word, amount_pages=self.amount_pages)
        session.add(word)
        user = User(chat_id=self.uid, words=[word])
        session.add(user)
        print("session.new", session.new)
        session.commit()
        session.close()

    def add_word(self, user):
        word = Word(word=self.word, amount_pages=self.amount_pages)
        user.words.append(word)
        session.add(user)
        print("session.new", session.new)
        session.commit()
        session.close()

    def sync_db(self):
        user = session.query(User).filter_by(chat_id=self.uid)
        if not user.first():
            self.create_user()
            return
        if user.filter(User.words.any(word=self.word)).first():
            # words exists, what to do?
            return
        self.add_word(user)

    @lru_cache
    def jokefunc(self):
        for joke in self.jokes:
            yield joke.text
