import transitions

from ane_searcher_bot.parser import a_joke
from .cache import cache


class FSM(object):
    def __init__(self, notify_method=None):
        states = [
            'start',
            transitions.State('word', ignore_invalid_triggers=True),
            'telling'
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
                'trigger': 'search_word_for_get_joke', # ignored
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
        ]

        self.dialogs = {
            'start': '{swear}Рассказать анекдот?',
            'word': 'Давай тему: слово или фраза',
            'telling': 'Ещё {word}?',

        }
        self.machine = transitions.Machine(
            model=self, states=states, initial='start', transitions=transition,
            send_event=True
        )
        self.word = None
        #self.notify_method = notify_method
        self.joke = None
        self.swear = ''


    def get_dialog(self):
        print(" get_dialog self.state", self.state)

        answer = self.dialogs[self.state].format(
            word=self.word, swear=self.swear)
        if self.joke:
            return self.joke + answer
        self.swear = ''
        return answer

    # def store_word(self, event_data):
    #     self.word = event_data.event.name
    #     print("self.word\n"*4, self.word)
    #     print("event_data", event_data, "event_data.event", event_data.event)

    def store_word(self, message, client_id):
        self.word = message
        self.client_id = client_id
        print("self.word\n"*4, self.word)

    def nexter(self, _):
        """
        print("nexter(self, _) self.word", self.word)
        joke = next(a_joke(self.word)) + '\n'
        print("cache info ", )
        self.joke = joke
        """
        joke = cache.last_user_word_function(self.client_id)
        return joke


    def notify(self, _):
        print("def notify(self, _):", )
        if self.notify_method is not None:
            self.notify_method(self.word)
            print("def notify(self, _):", self.notify_method)
        return 'a[a[a[a'

    # def notify(self, _):
    #     print("self.notify_method ", self.notify_method)
    #     if self.notify_method is not None:
    #         self.notify_method(self.size, self.pay_method)

    def reset(self, _):
        self.joke = None
        a_joke.cache_clear()
        self.swear = 'Пидора ответ.\n'