from functools import lru_cache

from bs4 import BeautifulSoup
from requests_html import HTMLSession
from urllib.parse import urljoin

from ane_searcher_bot.consts import PHRASE_URL, WORD_URL


def get_url(word, page=1):
    # if word phrase
    if ' ' in word:
        url = PHRASE_URL
    else:
        url = WORD_URL
    return url.format(word, page)


def get_jokes(word, page=1, amount_pages=0):
    session = HTMLSession()
    url = get_url(word=word, page=page)
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'lxml')  # "html.parser"
    jokes = soup.find_all("div", {"class": "text"})
    if not amount_pages:
        pageslist = soup.find_all("div", {"class": "pageslist"})
        if pageslist:
            amount_pages = tuple(filter(lambda x: x.isdigit(),
                                        pageslist[0].text))[-1]
            amount_pages = int(amount_pages)
    return jokes, amount_pages


@lru_cache
def a_joke(word, page=1, index=0):
    jokes, amount_pages = get_jokes(word, page)
    try:
        for joke in jokes[index:]:
            # print(joke.text)
            yield joke.text
    except StopIteration:
        if amount_pages - page > 1:
            return a_joke(word, page + 1)
