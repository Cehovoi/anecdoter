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


class TeleConnector:
    # def __init__(self, token, admin_id):
    #     self.teleconnector = telebot.TeleBot(token, parse_mode=None)
    #     self.admin_id = admin_id
    #
    # def run(self):
    #     print('in run')
    #
    #
    #     @self.teleconnector.message_handler(commands=['start'])
    #     def start(message):
    #         print('in start')
    #         self.teleconnector.send_message(message.from_user.id, 'Привет')
    #
    #     @self.teleconnector.message_handler(content_types=['text'])
    #     def send(message):
    #         self.teleconnector.send_message(message.from_user.id, 'Манда')
    #
    #     self.teleconnector.polling(none_stop=True)
    @classmethod
    def run(cls, json_hook=''):
        print('in run')

        @cls.connector.message_handler(commands=['start'])
        def start(message):
            print('in start')
            cls.connector.send_message(message.from_user.id, 'Привет')

        @cls.connector.message_handler(content_types=['text'])
        def send(message):
            print("message", message.text)
            cls.connector.send_message(message.from_user.id, 'Манда')

        #cls.connector.polling(none_stop=True)

        WEB_HOOK_URL = 'https://4572-176-53-210-25.eu.ngrok.io/webhook'
        cls.connector.remove_webhook()
        import time
        time.sleep(1)
        cls.connector.set_webhook(url=WEB_HOOK_URL)

        if json_hook:
            update = tele_types.Update.de_json(json_hook)
            cls.connector.process_new_updates([update])
        # command = ''
        # while command != 'stop':
        #     command = input('enter the message: ')
        #     TeleConnector.connector.process_new_updates([command])


