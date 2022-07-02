from bs4 import BeautifulSoup
from requests_html import HTMLSession

from ane_searcher_bot.contoller import Combiner


def dic_shortener(original_dict, needless_keys):
    return {key: value for key, value in
            original_dict if key not in needless_keys}


class Cache:
    def __init__(self):
        self._cache = {}

    def get_user_cache(self, uid):
        if uid not in self._cache:
            self._cache[uid] = {}
        return self._cache[uid]

    def _set_user_word(self, uid, word=None, user_cache=None):
        """
          Setting user word for example
        """
        if not user_cache:
            user_cache = self.get_user_cache(uid)
        else:
            # start parser with updated joke_index and page_num
            combiner = Combiner(**dic_shortener(user_cache.items(),
                                                ('state', 'word_f')))
            combiner.run_parser()
        cache_word = user_cache.get('word')
        if not cache_word:
            # create or read db record
            combiner = Combiner(uid, word)
            combiner.sync_db()
        else:
            # cache_word != word
            # save joke_index and page_num old word to db
            combiner = Combiner(**dic_shortener(user_cache.items(),
                                                ('state', 'word_f')))
            combiner.sync_db(change_word=True)
            # start parser and add new word to db
            combiner = Combiner(uid, word)
            combiner.sync_db()
        user_cache.update(dic_shortener(combiner.__dict__.items(), 'jokes'))
        user_cache['word_f'] = combiner.jokefunc()
        self._cache[uid] = user_cache

    def last_user_word(self, uid):
        user_cache = self.get_user_cache(uid)
        if not user_cache.get('last_word'):
            # TODO: Here should be request to DB to get user's last word
            # for now it is a mock
            user_cache['last_word'] = 'жопа'
        return user_cache['last_word']

    def last_user_word_function(self, uid):
        user_cache = self.get_user_cache(uid)
        try:
            joke = next(user_cache['word_f'])
            user_cache['joke_index'] += 1
        except StopIteration:
            user_cache['page_num'] += 1 # jump on new page
            user_cache['joke_index'] = 0 # reset because new page
            if user_cache['page_num'] <= user_cache['amount_pages']:
                self._set_user_word(uid, word=user_cache['word'],
                                    user_cache=user_cache)
                joke = self.last_user_word_function(uid)  # recursion!
            else:
                user_cache['page_num'] = 1
                joke = 'Анекдоты закончились, все пойдет заново'
        return joke

    def update_state(self, uid, state):
        self._cache[uid]['state'] = state


cache = Cache()
