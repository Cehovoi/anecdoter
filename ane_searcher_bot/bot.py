from .fsm import FSM
import transitions

from .cache import cache



class Listeners:
    def __init__(self):
        self._storage = {}

    def get(self, id):
        return self._storage.get(id)

    def set(self, id, state,):
        self._storage[id] = state
    #TODO поля для базы:
    # id (chat.id),
    # state (возможно после того как выталкнет из кэша)
    # word (чтобы можно было продолжить ту же тему после перерыва)
    # page (номер страницы с анекдотами на сайте)
    # anecdot_index (порядковый номер анекдота)



class Bot:
    def __init__(self, fsm=FSM, storage=Listeners()):
        self.fsm = fsm
        self.storage = storage

    def notify(self, word):
        print(f" joking word'{word}'")

    def handle(self, client_id, message):
        state = self.storage.get(client_id)
        message = message.lower().strip()
        if state is None:
            state = self.fsm(notify_method=self.notify)
            self.storage.set(client_id, state)
            return state.get_dialog()
        try:
            if state.state == 'word':
                state.store_word(message, client_id)
                cache._set_user_word(client_id, message)
                state.trigger('search_word_for_get_joke')
            else:
                state.trigger(message)
            self.storage.set(client_id, state)
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


