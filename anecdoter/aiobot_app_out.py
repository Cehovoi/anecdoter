import logging
import os
import ssl

from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.webhook import SendMessage
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageNotModified
from aiogram.utils.executor import start_webhook
from aiogram.utils.callback_data import CallbackData

from .consts import BLOCK_TRIGGER, SEARCH_TRIGGER, GRADE, RATING, DOMAIN
from .contoller import get_admin_rights
from .fsm import FSM
from .cache import cache
from .tools import string_formatter

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=cache)
dp.middleware.setup(LoggingMiddleware())
web_hook_host = os.getenv('HOOK_HOST') or f'https://{DOMAIN}'
web_hook_path = '/webhook'
web_hook_url = f'{web_hook_host}{web_hook_path}'
user_cb = CallbackData('user', 'action', 'amount')
admin_cb = CallbackData('admin', 'action')


class Form(StatesGroup):
    word = State()  # Will be represented in storage as 'Form:name'
    telling = State()  # Will be represented in storage as 'Form:age'


def ssl_connect():
    cert = os.path.abspath('nginx/.ssl/fullchain.pem')
    key = os.path.abspath('nginx/.ssl/privkey.pem')
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(cert, key)
    return context


def get_button(title, action, amount):
    button = types.InlineKeyboardButton(
        title,
        callback_data=user_cb.new(action=action, amount=amount)
    )
    return button


def get_confirm_buttons(joke_word=''):
    more_button = get_button(
        title=f'Ещё {joke_word}',
        action='more',
        amount=0
    )
    new_joke_button = get_button(
        title='Новый анекдот',
        action='new',
        amount=0
    )
    return more_button, new_joke_button


def get_ratting_buttons():
    buttons = [get_button(
        title=GRADE * var,
        action=f'ratting',
        amount=var,
    )
        for var in range(1, 6)]
    return buttons


def get_admin_keyboard():
    markup = types.InlineKeyboardMarkup()
    show_button = types.InlineKeyboardButton(
        'Посмотреть кэш',
        callback_data=admin_cb.new(action='show_cache')
    )
    sync_button = types.InlineKeyboardButton(
        'Сбросить кэш в базу',
        callback_data=admin_cb.new(action='sync_db')
    )
    stat_button = types.InlineKeyboardButton(
        'Посмотреть статистику',
        callback_data=admin_cb.new(action='show_stat')
    )
    markup.row(show_button, sync_button)
    markup.row(stat_button)
    return markup


admin_keyboard = get_admin_keyboard()
ratting_buttons = get_ratting_buttons()


def get_user_keyboard(joke_word):
    markup = types.InlineKeyboardMarkup()
    markup.row(*ratting_buttons[:3])
    markup.row(*ratting_buttons[-2:])
    confirm_buttons = get_confirm_buttons(joke_word)
    more_button = confirm_buttons[0]
    new_joke_button = confirm_buttons[1]
    markup.row(more_button, new_joke_button)
    return markup


@dp.message_handler(commands='admin')
async def cmd_admin_enter(message: types.Message):
    admin = get_admin_rights(message.from_id)
    if not admin:
        await message.reply('У тебя нет на это власти!')
    else:
        await message.reply('Сугубо админские кнопки',
                            reply_markup=admin_keyboard)


@dp.callback_query_handler(admin_cb.filter(action='show_cache'))
async def admin_show_cache(query: types.CallbackQuery):
    all_user_cache = cache._cache
    cache_list = [(key,
                   value.get('word'),
                   ('Всего страниц', value.get('amount_pages')),
                   ('Номер анекдота', value.get('joke_index')),
                   ('Номер страницы', value.get('page_num')))
                  for key, value in all_user_cache.items()]
    await bot.edit_message_text(
        f'Всего народа {len(all_user_cache)}\n'
        f'Кэшик каждого\n {cache_list}',
        query.from_user.id,
        query.message.message_id,
        reply_markup=admin_keyboard)


@dp.callback_query_handler(admin_cb.filter(action='sync_db'))
async def admin_sync_db(query: types.CallbackQuery):
    status = cache.drop_all_cache_to_db()
    await bot.edit_message_text(
        f'Чё там база говорит? - {status}',
        query.from_user.id,
        query.message.message_id,
        reply_markup=admin_keyboard)


@dp.callback_query_handler(admin_cb.filter(action='show_stat'))
async def admin_show_stat(query: types.CallbackQuery):
    address = DOMAIN + f'/login/{query.from_user.id}'
    await bot.edit_message_text(
        f'Пиздуйка ты на сайт {address}',
        query.from_user.id,
        query.message.message_id,
        reply_markup=admin_keyboard)


@dp.message_handler(state='*', commands='start')
async def cmd_start(message: types.Message, state: FSMContext):
    """
    Conversation's entry point
    """
    # Set state
    logging.info(f'current cache dict {cache.data}')
    await Form.word.set()
    await message.reply("Давай тему: слово или словосочетание")


# !!!! TExt
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Конец!', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Form.word)
async def process_new_word(message: types.Message, state: FSMContext):

    chat_id = message.chat.id
    joke_word = message.text
    # markup = get_user_keyboard(user_cb, joke_word=joke_word)
    markup = get_user_keyboard(joke_word)

    # logging.info(f'BEFORE state.get.data - {data}')
    #req = cache._set_user_word(chat_id, joke_word)
    # await state.update_data(uid=req)
    await state.set_data(data=dict(word=joke_word))
    # current_state = await state.get_state()
    joke = await state.get_data()
    logging.info(f'process_word joke {joke}, typr joke {type(joke)}')
    await Form.next()
    # await message.reply("Анекдот тут!\n" * 3, reply_markup=markup)
    return SendMessage(chat_id,
                       joke,
                       reply_markup=markup)


@dp.callback_query_handler(user_cb.filter(action='more'), state=Form.telling)
async def process_next_word(query: types.CallbackQuery, state: FSMContext):
    markup = query.message.reply_markup
    # when wee get to this from ratting state ratting_buttons haven`t in markup
    if len(markup['inline_keyboard']) == 1:
        logging.info(f'ratting_buttons {ratting_buttons}')
        markup['inline_keyboard'].insert(0, ratting_buttons[-2:])
        markup['inline_keyboard'].insert(0, ratting_buttons[:3])
    # logging.info(f'process_next_word markup - {markup}')

    joke = await state.get_data()
    # to reply to previos message
    # await query.message.reply("Анекдот тут!")
    logging.info(f'process_next_word joke {joke}, typr joke {type(joke)}')
    # to edit message
    # await bot.edit_message_text(text='',
    # query.from_user.id, query.message.message_id,)

    await query.message.answer(text=joke,
                               reply_markup=markup,
                               )


@dp.callback_query_handler(user_cb.filter(action='more'), state=Form.word)
async def process_next_word(query: types.CallbackQuery):
    await bot.edit_message_text(text="Придётся писать!",
                                chat_id=query.from_user.id,
                                message_id=query.message.message_id)


@dp.callback_query_handler(user_cb.filter(action='new'), state=Form.telling)
async def process_next_word(query: types.CallbackQuery, state: FSMContext):
    # save progress with word to db
    await Form.word.set()
    await query.message.answer("Давай тему: слово или словосочетание",
                               # reply_markup=user_keyboard,
                               )


@dp.callback_query_handler(user_cb.filter(action='ratting'), state=Form.telling)
async def process_ratting_joke(query: types.CallbackQuery,
                               callback_data: dict,
                               state: FSMContext):
    markup = query.message.reply_markup
    # delete ratting_buttons from markup
    markup['inline_keyboard'].pop(0)
    markup['inline_keyboard'].pop(0)
    logging.info(f'process_ratting_joke query --- {query}')

    message_id = query.message.message_id
    logging.info(f'process_ratting_joke message_id -- {message_id}')
    # check if message already ratted by user
    if message_id == 4616:
        logging.info(f'if message_id == 4616')
        text = f"Анекдот уже оценен!"

    else:
        # some operations with db
        text = f"Анекдот добавлен на сайт c рейтингом {callback_data['amount']}"
    await query.message.reply(
        text=text,
        reply_markup=markup,
    )


@dp.errors_handler(exception=MessageNotModified)
async def message_not_modified_handler(update, error):
    # for skipping this exception
    return True


async def on_startup(dp):
    await bot.set_webhook(web_hook_url)
    # insert code here to run it after start


async def on_shutdown(dp):
    logging.warning('Shutting down..')
    status = cache.drop_all_cache_to_db()
    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()
    logging.warning(f'{status}\nBye!')


async def setup_bot_commands(dp):
    bot_commands = [
        types.BotCommand(command='/start', description='Поехали!'),
        types.BotCommand(command='/cancel', description='Хорош!'),
        types.BotCommand(command="/help", description="Get info about me"),
        types.BotCommand(command="/qna", description="set bot for a QnA task"),
        types.BotCommand(command="/chat", description="set bot for free chat"),

    ]
    await bot.set_my_commands(bot_commands)


def start_aiobot():
    web_app_host = '0.0.0.0'
    web_app_port = os.getenv('BOT_PORT') or 8443
    # for local regime, ngrok have his ssl
    context = ssl_connect() if DOMAIN in web_hook_host else None
    start_dict = dict(
        dispatcher=dp,
        webhook_path=web_hook_path,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=web_app_host,
        port=web_app_port,
        ssl_context=context,
    )
    try:
        start_webhook(**start_dict)
    except Exception as e:
        status = cache.drop_all_cache_to_db()
        logging.warning("AIOBOT fell -- ", e, 'drop to db', status)
