import transitions
from .cache import cache
from .consts import DOES_NOT_EXISTS, RATING, SEARCH_TRIGGER, RATE_TRIGGER, \
    BLOCK_TRIGGER, SITE, INVITATION


class FSM(object):
    def __init__(self):
        states = [
            'start',
            transitions.State('word', ignore_invalid_triggers=True),
            'telling',
            'one_more',
        ]
        transition = [
            {
                'trigger': 'да',
                'source': 'start',
                'dest': 'word',

            },
            {
                'trigger': 'нет',
                'source': 'start',
                'before': 'reset',
                'dest': 'start',
            },
            {
                'trigger': BLOCK_TRIGGER,
                'source': 'word',
                'after': 'reset',
                'dest': 'word',
            },
            {
                'trigger': SEARCH_TRIGGER,  # ignored
                'source': 'word',
                'dest': 'telling',
                'after': 'nexter',

            },
            {
                'trigger': 'да',
                'source': 'telling',
                'dest': 'telling',
                'after': 'nexter',

            },
            {
                'trigger': 'нет',
                'source': 'telling',
                'before': 'reset',
                'dest': 'start',

            },
            {
                'trigger': RATE_TRIGGER,
                'source': 'telling',
                'dest': 'one_more',
                'after': 'reset',

            },
            {
                'trigger': 'да',
                'source': 'one_more',
                'dest': 'telling',
                'after': 'nexter',


            },
            {
                'trigger': 'нет',
                'source': 'one_more',
                'before': 'reset',
                'dest': 'start',

            },
        ]

        self.dialogs = {
            'start': '{swear}Рассказать анекдот?',
            'word': 'Давай тему: слово или фраза',
            'telling': '\n\nЕщё {word}?\n\n' + RATING,
            'one_more': 'Ещё {word}?'
        }
        self.machine = transitions.Machine(
            model=self, states=states, initial='start', transitions=transition,
            send_event=True
        )
        self.word = None
        self.joke = None
        self.swear = ''

    def get_dialog(self):
        answer = self.dialogs[self.state].format(
            word=self.word, swear=self.swear)
        if self.joke:
            return self.joke + answer
        self.swear = ''
        return answer

    def store_word(self, message, client_id):
        self.word = message
        self.client_id = client_id

    def nexter(self, _):
        joke = cache.last_user_word_function(self.client_id)
        if not joke:
            self.joke = None
            self.swear = DOES_NOT_EXISTS + '\n'
            self.state = 'start'
            return
        self.joke = joke
        return joke

    def reset(self, event_data):
        print("dir(self)", dir(self))
        print("self.word", self.word)
        if event_data.event.name == BLOCK_TRIGGER:
            self.joke = BLOCK_TRIGGER + '\n'
        if event_data.event.name == RATE_TRIGGER:
            print('self.client_id', self.client_id)
            self.joke = INVITATION + SITE.format(4, self.client_id) + '\n'
        else:
            self.swear = 'Пидора ответ.\n'
            self.joke = None