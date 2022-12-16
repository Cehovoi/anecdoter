from functools import lru_cache

from bs4 import BeautifulSoup
from requests_html import HTMLSession
from urllib.parse import urljoin

from anecdoter.consts import PHRASE_URL, WORD_URL


class DoesNotExists(Exception):
    pass


def get_url(word, page=1):
    # if word phrase
    if ' ' in word:
        url = PHRASE_URL
    else:
        url = WORD_URL
    return url.format(word, page)


def get_jokes(word, page=1):
    session = HTMLSession()
    url = get_url(word=word, page=page)
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'lxml')  # "html.parser"
    jokes = soup.find_all("div", {"class": "text"})
    pageslist = soup.find_all("div", {"class": "pageslist"})
    if not pageslist:
        raise DoesNotExists
    amount_pages = max(tuple(
        int(i.text) for i in pageslist[0] if i.text.isdigit()
    ))
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
