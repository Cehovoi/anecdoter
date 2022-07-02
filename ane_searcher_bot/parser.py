from functools import lru_cache

from bs4 import BeautifulSoup
from requests_html import HTMLSession
from urllib.parse import urljoin


def get_url(word, page=1):
    # if word phrase
    if ' ' in word:
        # mode=phrase # search exact phrase
        # mode=all # occurrence all words in phrase
        # mode=any # occurrence any word  in phrase
        url = 'https://www.anekdot.ru/search/?query={}&xcnt=20&mode=all&ch[j]=on&page={}'
    else:
        url = 'https://www.anekdot.ru/search/?query={}&ch[j]=on&page={}'
    return url.format(word, page)


def get_jokes(word, page=1, amount_pages=0):
    session = HTMLSession()
    url = get_url(word=word, page=page)
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'lxml')  # "html.parser"
    jokes = soup.find_all("div", {"class": "text"})
    if not amount_pages:
        pageslist = soup.find_all("div", {"class": "pageslist"})
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
