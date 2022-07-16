from functools import lru_cache

from ane_searcher_bot.parser import get_jokes





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
        from ane_searcher_bot import create_app
        create_app().app_context().push()
        from ane_searcher_bot import db
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
            self.save(word, db)

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
                    self.save(word, db)
                    return
                user = User(chat_id=self.uid)
                self.save([word, user],db, multi=True)

    @staticmethod
    def save(obj, db, multi=False):
        if multi:
            db.session.add_all(obj)
        else:
            db.session.add(obj)
        db.session.commit()
        db.session.close()

    @lru_cache
    def jokefunc(self):
        for joke in self.jokes:
            yield joke.text
