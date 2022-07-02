from .fsm import FSM
import transitions

from .cache import cache
from .tools import string_formatter


class Bot:
    def __init__(self, fsm=FSM, storage=cache):
        self.fsm = fsm
        self.storage = storage

    def notify(self, word):
        print(f" joking word'{word}'")

    def handle(self, client_id, message):
        state = self.storage.get_user_cache(client_id)
        message = string_formatter(string_formatter)
        if not state:
            state = self.fsm(notify_method=self.notify)
            self.storage.update_state(client_id, state)
            return state.get_dialog()
        try:
            state = state['state']
            if state.state == 'word':
                print("state word\n"*5)
                state.store_word(message, client_id)
                self.storage._set_user_word(client_id, message)
                state.trigger('search_word_for_get_joke')
            else:
                state.trigger(message)
            self.storage.update_state(client_id, state)
        except Exception as e:
            # if '/' in e:
            #     pass
            print("Exception!!!", e)
            s = state.machine.get_triggers(state.state)
            answer = list(filter(lambda x: not x.startswith('to_'), s))
            word = ''.join(word + ' ' for word in answer)
            return 'Можно ответить: ' + word
        answer = state.get_dialog()
        return answer


