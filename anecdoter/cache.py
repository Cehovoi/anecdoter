from collections import OrderedDict

from anecdoter.consts import SIZE_OF_CASH, END_WARNING, \
    NEEDLESS_KEYS
from anecdoter.contoller import Combiner, RatingFill
from anecdoter.tools import dic_shortener


class Cache:
    def __init__(self):
        self._cache = OrderedDict()

    def get_user_cache(self, uid):
        """
            Create, find and push to db user cache when SIZE_OF_CASH full.
        """
        if uid not in self._cache:
            self._cache[uid] = {}
        if len(self._cache) == SIZE_OF_CASH:
            user_cache = self._cache.popitem(last=False)
            self._drop_cache_to_db(user_cache[1])
        return self._cache[uid]

    def drop_all_cache_to_db(self):
        users_cache = self._cache
        if not users_cache:
            return 'Nothing_to_drop_cache_is_empty'
        for num, user_cache in enumerate(users_cache.values()):
            self._drop_cache_to_db(user_cache)
        return f'Dropped_cache_of_{num}_users'

    @staticmethod
    def _drop_cache_to_db(user_cache):
        combiner = Combiner(**dic_shortener(user_cache.items(),
                                            NEEDLESS_KEYS))
        combiner.sync_db(change_word=True)

    def set_user_word(self, uid, word):
        self._set_user_word(uid, word)

    def _set_user_word(self, uid, word=None, user_cache=None):
        """
          Fill user cache.
          Create Combiner instance for parsing and save to db.
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

        rating = RatingFill(word=user_cache['word'],
                            joke=user_cache['joke'],
                            grade=len(message))
        rating.update_db()

    def last_user_word_function(self, uid):
        """
            Run joke generator.
            Create new user_cache and recall himself when generator is over.
         """
        user_cache = self.get_user_cache(uid)
        if not user_cache['jokes_len']:
            # by the word bot doesn`t find any joke, clear the user cache
            self._cache[uid] = {}
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
                joke = END_WARNING + '\n' + '\n' + joke
        user_cache['joke'] = joke
        return joke

    def update_state(self, uid, state):
        user_cache = self.get_user_cache(uid)
        user_cache['state'] = state


cache = Cache()
