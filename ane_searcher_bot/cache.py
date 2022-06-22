from bs4 import BeautifulSoup
from requests_html import HTMLSession

from ane_searcher_bot.contoller import Combiner


class Cache():
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
        # args = ['word', 'amount_pages',
        #         'joke_index', 'page_num', 'state']
        if not user_cache.get('word'):
            user_cache['word'] = word
            combiner = Combiner(uid, word)
            combiner.run_parser()
            combiner.sync_db()
            user_cache['amount_pages'] = combiner.amount_pages
            user_cache['page_num'] = combiner.page_num
            user_cache['joke_index'] = combiner.joke_index
        else:
            print("in else")
            print("user_cache", user_cache)
            combiner = Combiner(uid, **user_cache)
            combiner.run_parser()
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
        print('call!')
        user_cache = self.get_user_cache(uid)
        try:
            joke = next(user_cache['word_f'])
            user_cache['joke_index'] += 1
        except StopIteration:
            user_cache['page_num'] += 1
            if user_cache['page_num'] <= user_cache['amount_pages']:
                self._set_user_word(uid, user_cache=user_cache)
                self.last_user_word_function(uid)  # recursion!
            else:
                user_cache['page_num'] = 1
                joke = 'Анекдоты закончились, все пойдет заново'

        return joke

    def update_state(self, uid, state):
        self._cache[uid]['state'] = state


cache = Cache()
