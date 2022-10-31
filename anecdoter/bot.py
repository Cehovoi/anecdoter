from telebot import types as tele_types
from flask import request
from .consts import GRADE, SEARCH_TRIGGER, BLOCK_TRIGGER
from .fsm import FSM
from .cache import cache
from .tools import string_formatter


class Bot:
    def __init__(self, fsm=FSM, storage=cache):
        self.fsm = fsm
        self.storage = storage

    def handle(self, client_id, message):
        state = self.storage.get_user_cache(client_id)
        message = string_formatter(message)
        if not state:
            state = self.fsm()
            self.storage.update_state(client_id, state)
            return state.get_dialog()
        try:
            state = state['state']
            if state.state == 'word':
                if message == 'да' or message == 'нет':
                    state.trigger(BLOCK_TRIGGER)
                else:
                    state.store_word(message, client_id)
                    self.storage.set_user_word(client_id, message)
                    state.trigger(SEARCH_TRIGGER)
            elif state.state == 'telling' and GRADE in message:
                self.storage.set_user_grade(client_id, message)
                state.store_rate(message)
                state.trigger(GRADE)
            else:
                state.trigger(message)
            self.storage.update_state(client_id, state)
        except Exception as e:
            print("Exception!!!", e)
            s = state.machine.get_triggers(state.state)
            answer = list(filter(lambda x: not x.startswith('to_'), s))
            word = ''.join(word + ' ' for word in answer)
            return 'Можно ответить: ' + word
        answer = state.get_dialog()
        return answer


