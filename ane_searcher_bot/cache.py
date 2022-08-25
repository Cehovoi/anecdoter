from collections import OrderedDict

from ane_searcher_bot.consts import SIZE_OF_CASH, END_WARNING, DOES_NOT_EXISTS, \
    NEEDLESS_KEYS
from ane_searcher_bot.contoller import Combiner, RatingFill
from ane_searcher_bot.tools import dic_shortener


class Cache:
    def __init__(self):
        self._cache = OrderedDict()

    def get_user_cache(self, uid):
        if uid not in self._cache:
            self._cache[uid] = {}
        if len(self._cache) == SIZE_OF_CASH:
            first = self._cache.popitem(last=False)
            user_cache = first[1]
            combiner = Combiner(**dic_shortener(user_cache.items(),
                                                NEEDLESS_KEYS))
            combiner.sync_db(change_word=True)
        return self._cache[uid]

    def set_user_word(self, uid, word):
        self._set_user_word(uid, word)

    def _set_user_word(self, uid, word=None, user_cache=None):
        """
          Setting user word for example
        """
        if not user_cache:
            user_cache = self.get_user_cache(uid)
        else:
            # start parser with updated joke_index and page_num
            combiner = Combiner(**dic_shortener(user_cache.items(),
                                                NEEDLESS_KEYS))
            combiner.run_parser()
            user_cache['word_f'] = combiner.jokefunc()
            self._cache[uid] = user_cache
            return
        cache_word = user_cache.get('word')
        if not cache_word:
            # create or read db record
            combiner = Combiner(uid, word)
            combiner.sync_db()
        else:
            # cache_word != word
            # save joke_index and page_num old word to db
            combiner = Combiner(**dic_shortener(user_cache.items(),
                                                NEEDLESS_KEYS))
            combiner.sync_db(change_word=True)
            # start parser and add new word to db
            combiner = Combiner(uid, word)
            combiner.sync_db()
        user_cache.update(dic_shortener(combiner.__dict__.items(),
                                        ('jokes', 'joke')))
        user_cache['word_f'] = combiner.jokefunc()
        self._cache[uid] = user_cache

    def set_user_grade(self, uid, message):
        user_cache = self.get_user_cache(uid)
        print("def set_user_grade(self, uid): user_cache, message",
              user_cache, message)
        rating = RatingFill(word=user_cache['word'],
                            joke=user_cache['joke'],
                            grade=len(message))
        rating.update_db()


    def last_user_word_function(self, uid):
        user_cache = self.get_user_cache(uid)
        if not user_cache['jokes_len']:
            return
        try:
            joke = next(user_cache['word_f'])
            user_cache['joke_index'] += 1
        except StopIteration:
            # jump on new page
            user_cache['page_num'] += 1
            # reset because new page
            user_cache['joke_index'] = 0
            if user_cache['page_num'] <= user_cache['amount_pages']:
                self._set_user_word(uid, word=user_cache['word'],
                                    user_cache=user_cache)
                # recursion!
                joke = self.last_user_word_function(uid)
            else:
                user_cache['page_num'] = 1
                self._set_user_word(uid, word=user_cache['word'],
                                    user_cache=user_cache)
                # recursion!
                joke = self.last_user_word_function(uid)
                joke = END_WARNING + '\n' + joke
        user_cache['joke'] = joke
        return joke

    def update_state(self, uid, state):
        print('update_state(self, uid, state)')
        user_cache = self.get_user_cache(uid)
        user_cache['state'] = state
        print("user_cache", user_cache)


cache = Cache()
