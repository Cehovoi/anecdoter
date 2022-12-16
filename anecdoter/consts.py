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



AMOUNT_JOKES_FOR_RATING = 9


DOMAIN = 'anecdoter.su'
SITE = 'anecdoter.su/rating/{}/{}'

HELP_MESSAGE = 'Ты мне слово я тебе анекдот.\nАнекдот может быть бородатым ' \
               'и не смешным\nЗа это можешь поставить ему плохую оценку.\n' \
               'Все оценённые анекдоты попадают на сайт, ' \
               'куда можешь попасть и ты ' \
               'перейдя по ссылке после оценки.\n' \
               'А можешь пока не оценивать и либо ткнуть на кнопку "Ещё" ' \
               'либо написать новоё слово или фразу.\n' \
               'Жми на старт и поехали!'


LOGIN_ERROR = 'Admin panel only for those ' \
               'who use the bot.' \
               'Go to telegram and get your chat id.' \
               'Click on text to go back to rating jokes'
