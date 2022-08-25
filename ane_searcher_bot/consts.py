SIZE_OF_CASH = 4

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
