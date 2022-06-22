from bs4 import BeautifulSoup
from requests_html import HTMLSession

from ane_searcher_bot.contoller import Combiner

pageslist_amount = 0


def get_url(word, page=1):
    url = 'https://www.anekdot.ru/search/?query={}&ch[j]=on&page={}'.format(
        word, page)
    return url


def get_jokes(word, page=1):
    global pageslist_amount
    session = HTMLSession()
    url = get_url(word=word, page=page)
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'lxml')  # "html.parser"
    jokes = soup.find_all("div", {"class": "text"})
    if not pageslist_amount:
        pageslist = soup.find_all("div", {"class": "pageslist"})
        pageslist_amount = tuple(filter(lambda x: x.isdigit(),
                                        pageslist[0].text))[-1]
    print('text amount_pages', pageslist_amount)
    return jokes, pageslist_amount


class Cache():
    def __init__(self):
        self._cache = {}

    def get_user_cache(self, uid):
        if uid not in self._cache:
            self._cache[uid] = {}
        return self._cache[uid]

    def _set_user_word(self, uid, word):
        """
          Setting user word for example
        """
        user_cache = self.get_user_cache(uid)
        args = ['word', 'amount_pages',
                'joke_index', 'page_num', 'state']
        if not user_cache.get('word'):
            user_cache['word'] = word
            combiner = Combiner(uid, word)
            combiner.run_parser()
            combiner.sync_db()
        else:
            print("in else")
            # combiner = Combiner(uid, word, user_cache['amount_pages'],
            #                     user_cache['joke_index'],
            #                     user_cache['page_num'],
            #                     user_cache['state'])
            combiner = Combiner(uid, **dict(user_cache[key] for key in args))

            combiner.run_parser()
        user_cache.update({key: getattr(combiner, key)
                           for key in args})
        user_cache['word_f'] = combiner.jokefunc()
        self._cache[uid] = user_cache

    def last_user_word(self, uid):
        user_cache = self.get_user_cache(uid)
        if not user_cache.get('last_word'):
            # TODO: Here should be request to DB to get user's last word
            # for now it is a mock
            user_cache['last_word'] = 'жопа'
        return user_cache['last_word']

    def last_user_word_function(self, uid, jokes=None):
        print('call!')
        user_cache = self.get_user_cache(uid)
        try:
            joke = next(user_cache['word_f'])
        except StopIteration:
            user_cache['page_num'] += 1
            if user_cache['page_num'] <= user_cache['amount_pages']:
                pass
            else:
                user_cache['page_num'] = 1

        return joke

    def update_state(self, uid, state):
        self._cache[uid]['state'] = state


cache = Cache()
