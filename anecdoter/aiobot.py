import logging
from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.webhook import SendMessage
from aiogram.utils.executor import start_webhook
from aiogram.utils.callback_data import CallbackData

from .consts import BLOCK_TRIGGER, SEARCH_TRIGGER, GRADE, RATING
from .fsm import FSM
from .cache import cache
from .tools import string_formatter


def button(value):
    return types.KeyboardButton(value)


def collect_buttons(content, sequence):
    return tuple(button(content * i) for i in sequence)


def add_buttons(all_buttons=False, admin_button=False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if all_buttons:
        grade_buttons = collect_buttons(GRADE, range(1, 6))
        markup.row(*grade_buttons[:3])
        markup.row(*grade_buttons[-2:])
    markup.row(*collect_buttons(1, ('ДА', 'НЕТ')))
    if admin_button:
        markup.row(button('Админка'))
    return markup


class AioBot:

    def __init__(self,
                 token,
                 admin_id=None,
                 web_hook_host=None,
                 web_hook_path=None,
                 web_app_host=None,
                 web_app_port=None,
                 buttons={},
                 fsm=FSM,
                 storage=cache):
        self.token = token
        self.admin_id = admin_id
        self.web_hook_host = web_hook_host
        self.web_hook_path = web_hook_path
        self.web_app_host = web_app_host
        self.web_app_port = web_app_port
        self.buttons = buttons
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

    def run_aiogram(self):
        web_hook_url = f'{self.web_hook_host}{self.web_hook_path}'
        logging.basicConfig(level=logging.INFO)
        bot = Bot(token=self.token)
        dp = Dispatcher(bot)
        dp.middleware.setup(LoggingMiddleware())
        # admin_cb = CallbackData()
        vote_cb = CallbackData('vote', 'action', 'amount')

        def get_keyboard(amount):
            return types.InlineKeyboardMarkup().row(
                types.InlineKeyboardButton('👍', callback_data=vote_cb.new(
                    action='up', amount=amount)),
                types.InlineKeyboardButton('👎', callback_data=vote_cb.new(
                    action='down', amount=amount)))

        @dp.callback_query_handler(vote_cb.filter(action='up'))
        async def vote_up_cb_handler(query: types.CallbackQuery,
                                     callback_data: dict):
            logging.info(callback_data)
            amount = int(callback_data['amount'])
            amount += 1
            await bot.edit_message_text(
                f'You voted up! Now you have {amount} votes.',
                query.from_user.id,
                query.message.message_id,
                reply_markup=get_keyboard(amount))

        @dp.callback_query_handler(vote_cb.filter(action='down'))
        async def vote_down_cb_handler(query: types.CallbackQuery,
                                       callback_data: dict):
            amount = int(callback_data['amount'])
            amount -= 1
            await bot.edit_message_text(
                f'You voted down! Now you have {amount} votes.',
                query.from_user.id,
                query.message.message_id,
                reply_markup=get_keyboard(amount))



        @dp.message_handler()
        async def conversation(message: types.Message):
            chat_id = message.chat.id
            response = self.handle(chat_id, message.text)
            admins_chat = self.admin_id == chat_id
            if admins_chat:
                grades_confirm = 'admin_grades_confirm'
                confirm = 'admin_confirm'
            else:
                grades_confirm = 'grades_confirm'
                confirm = 'confirm'
            if response.endswith(RATING):
                markup = self.buttons[grades_confirm]
            elif response.endswith('?') or admins_chat:
                markup = self.buttons[confirm]
            else:
                markup = None
            return SendMessage(chat_id, response, reply_markup=get_keyboard(0))



        async def on_startup(dp):
            await bot.set_webhook(web_hook_url)
            # insert code here to run it after start

        async def on_shutdown(dp):
            logging.warning('Shutting down..')
            # insert code here to run it before shutdown
            # Remove webhook (not acceptable in some cases)
            await bot.delete_webhook()
            # Close DB connection (if used)
            await dp.storage.close()
            await dp.storage.wait_closed()
            logging.warning('Bye!')

        start_webhook(
            dispatcher=dp,
            webhook_path=self.web_hook_path,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=self.web_app_host,
            port=self.web_app_port,
        )

