from bs4 import BeautifulSoup
from requests_html import HTMLSession

def get_jokes(word, page=1):
	global pageslist_amount
	session = HTMLSession()
	url = get_url(word=word, page=page)
	response = session.get(url)
	soup = BeautifulSoup(response.text, 'lxml') #"html.parser"
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
        if not user_cache.get('last_word'):
           user_cache['last_word'] = word

        if not user_cache.get('last_word_f'):
            jokes, _ = get_jokes(word)
            # Эта функция должна выдаваться фабрикой
            def jokefunc(jokes):
                for joke in jokes:
                    yield joke.text
            user_cache['last_word_f'] = jokefunc(jokes)


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
        # if not user_cache.get('last_word_f'):
        #    user_cache['last_word_f'] = lambda: [
        #        (yield joke.text) for joke in jokes
        #    ]
        return user_cache['last_word_f']()


cache = Cache()