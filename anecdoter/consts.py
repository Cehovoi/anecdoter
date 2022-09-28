SIZE_OF_CASH = 10

# mode=phrase # search exact phrase
# mode=all # occurrence all words in phrase
# mode=any # occurrence any word  in phrase
PHRASE_URL = 'https://www.anekdot.ru/search/?query={}&xcnt=20&mode=all&ch[j]=on&page={}'
WORD_URL = 'https://www.anekdot.ru/search/?query={}&ch[j]=on&page={}'

END_WARNING = 'Анекдоты на эту тему закончились, но не отчаивайся повторение мать заикания!'

DOES_NOT_EXISTS = 'Анекдота на эту тему похоже в природе не существует.'

RATING = 'Только сначала нажми на кнопку и оцени анекдот!'

GRADE = '★'

NEEDLESS_KEYS = ('state', 'word_f', 'joke')

AMOUNT_JOKES_FOR_RATING = 9

SEARCH_TRIGGER = 'search_word_for_get_joke'

BLOCK_TRIGGER = 'ДА и НЕТ в данном случае не уместны'



SITE = 'https://anecdoter-web.herokuapp.com/rating/{}/{}'

INVITATION = 'Спасибо за контент, анекдот добавлен на сайт, ' \
             'зайди и посмотри анекдоты с ' \
             'таким же рейтингом.\n'


