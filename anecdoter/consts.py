SIZE_OF_CASH = 10

# mode=phrase # search exact phrase
# mode=all # occurrence all words in phrase
# mode=any # occurrence any word  in phrase
PHRASE_URL = 'https://www.anekdot.ru/search/?query={}&xcnt=20&mode=all&ch[j]=on&page={}'
WORD_URL = 'https://www.anekdot.ru/search/?query={}&ch[j]=on&page={}'

DOES_NOT_EXISTS = 'Анекдота на эту тему похоже в природе не существует.'

JOKES_OVER = 'Шутки в сторону... на эту тему они закончились и пойдут заново'

ONE_MORE = 'Ещё'

GRADE = '★'

NEEDLESS_KEYS = ('state', 'word_f', 'joke')

AMOUNT_JOKES_FOR_RATING = 9


DOMAIN = 'anecdoter.su'
SITE = 'anecdoter.su/rating/{}/{}'




LOGIN_ERROR = 'Admin panel only for those ' \
               'who use the bot.' \
               'Go to telegram and get your chat id.' \
               'Click on text to go back to rating jokes'

END_WARNING = 'Анекдоты на эту тему закончились, но не отчаивайся повторение мать заикания!'

RATING = 'Только сначала нажми на кнопку и оцени анекдот!'

SEARCH_TRIGGER = 'search_word_for_get_joke'

BLOCK_TRIGGER = 'ДА и НЕТ в данном случае не уместны'

INVITATION = 'Спасибо за контент, анекдот добавлен на сайт, ' \
             'зайди и посмотри анекдоты с ' \
             'таким же рейтингом.\n'
