from functools import lru_cache

from bs4 import BeautifulSoup
from requests_html import HTMLSession
from urllib.parse import urljoin


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
	soup = BeautifulSoup(response.text, 'lxml') #"html.parser"
	jokes = soup.find_all("div", {"class": "text"})
	if not pageslist_amount:
		pageslist = soup.find_all("div", {"class": "pageslist"})
		pageslist_amount = tuple(filter(lambda x: x.isdigit(),
										pageslist[0].text))[-1]
	print('text amount_pages', pageslist_amount)
	return jokes, pageslist_amount

@lru_cache
def a_joke(word, page=1, index=0):
	jokes, amount_pages = get_jokes(word, page)
	try:
		for joke in jokes[index:]:
			#print(joke.text)
			yield joke.text
	except StopIteration:
		if amount_pages - page > 1:
			return a_joke(word, page+1)






if __name__ == '__main__':
	g = get_jokes('пися')
	while True:
		try:
			print(next(g))
		except StopIteration:
			print('ВСЁ!')
			break