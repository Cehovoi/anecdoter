import logging
import os
import ssl
from datetime import datetime

from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.webhook import SendMessage
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageNotModified
from aiogram.utils.executor import start_webhook
from aiogram.utils.callback_data import CallbackData

from .consts import GRADE, DOMAIN, DOES_NOT_EXISTS, ONE_MORE
from .contoller import get_admin_rights
from .parser import DoesNotExists
from .cache import cache

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
        title=f'{ONE_MORE} {joke_word}',
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


def get_invite_button(amount):
    date = datetime.now().isoformat(sep=" ", timespec="seconds")
    invite_button = types.InlineKeyboardButton(
        text=f'{GRADE * amount}, {date}, на сайт 👆',
        callback_data=user_cb.new(action='invite', amount=0),
        url=f'{DOMAIN}/rating/{amount}/1',
    )
    return invite_button


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


@dp.message_handler(state='*', commands='admin')
async def cmd_admin_enter(message: types.Message):
    admin = get_admin_rights(message.from_id)
    if not admin:
        await message.reply('У тебя нет на это власти!')
    else:
        await message.reply('Сугубо админские кнопки',
                            reply_markup=admin_keyboard)


@dp.callback_query_handler(admin_cb.filter(action='show_cache'), state='*')
async def admin_show_cache(query: types.CallbackQuery):
    all_user_cache = cache.data
    logging.info(f'all_user_cache {all_user_cache}')
    cache_list = [(key,
                   value[key]['data'].get('word'),
                   ('Всего страниц', value[key]['data'].get('amount_pages')),
                   ('Номер анекдота', value[key]['data'].get('joke_index')),
                   ('Номер страницы', value[key]['data'].get('page_num')))
                  for key, value in all_user_cache.items()]
    await bot.edit_message_text(
        f'Всего народа {len(all_user_cache)}\n'
        f'Кэшик каждого\n {cache_list}',
        query.from_user.id,
        query.message.message_id,
        reply_markup=admin_keyboard)


@dp.callback_query_handler(admin_cb.filter(action='sync_db'), state='*')
async def admin_sync_db(query: types.CallbackQuery):
    status = cache.drop_all_cache_to_db()
    await bot.edit_message_text(
        f'Чё там база говорит? - {status}',
        query.from_user.id,
        query.message.message_id,
        reply_markup=admin_keyboard)


@dp.callback_query_handler(admin_cb.filter(action='show_stat'), state='*')
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
    await Form.word.set()
    await message.answer("Давай тему: слово или фразу")


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
    await state.finish()
    await message.answer("Не смешно...")


@dp.message_handler(lambda message: not all(
    [word.isalpha() for word in message.text.strip().split(' ')]),
                    state=Form.word)
async def process_new_word_invalid(message: types.Message):
    """
    If word is invalid
    """
    return await message.reply(
        "Никаих цифр или знаков препинания, только слово или несколько слов!")


@dp.message_handler(state=Form.word)
async def process_new_word(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    joke_word = message.text
    markup = get_user_keyboard(joke_word)
    logging.info(f'message {message}')
    try:
        await state.set_data(data=dict(word=joke_word,
                                       username=message.chat.username))
    except DoesNotExists:
        return SendMessage(chat_id, DOES_NOT_EXISTS)
    joke = await state.get_data()
    await Form.next()
    return SendMessage(chat_id, joke, reply_markup=markup)


@dp.callback_query_handler(user_cb.filter(action='more'), state=Form.word)
async def process_next_word(query: types.CallbackQuery):
    await query.message.answer("Пишем ручками слово или фразу")


@dp.callback_query_handler(user_cb.filter(action='more'), state=Form.telling)
async def process_next_word(query: types.CallbackQuery, state: FSMContext):
    message_id = query.message.message_id
    message_text = query.message.text
    markup = query.message.reply_markup
    confirm_buttons = markup['inline_keyboard'].pop()
    await bot.edit_message_text(text=message_text,
                                chat_id=query.from_user.id,
                                message_id=message_id,
                                reply_markup=markup)
    # if joke already rated
    if len(markup['inline_keyboard']) == 1:
        # remove grade button with link to site
        markup['inline_keyboard'].pop()
        markup['inline_keyboard'].insert(0, ratting_buttons[-2:])
        markup['inline_keyboard'].insert(0, ratting_buttons[:3])
    markup['inline_keyboard'].append(confirm_buttons)
    try:
        joke = await state.get_data()
    except KeyError:
        await state.set_data(data=dict(
            word=confirm_buttons[0]["text"][len(ONE_MORE) + 1:],
            username=query.message.chat.username))
        joke = await state.get_data()
    await query.message.answer(text=joke, reply_markup=markup)


@dp.callback_query_handler(user_cb.filter(action='new'), state=Form.word)
async def process_next_word(query: types.CallbackQuery):
    await query.message.answer("Придётся писать!")


@dp.callback_query_handler(user_cb.filter(action='new'), state=Form.telling)
async def process_next_word(query: types.CallbackQuery):
    # save progress with word to db
    message_id = query.message.message_id
    message_text = query.message.text
    markup = query.message.reply_markup
    markup['inline_keyboard'].pop(len(markup['inline_keyboard']) - 1)
    await bot.edit_message_text(text=message_text,
                                chat_id=query.from_user.id,
                                message_id=message_id,
                                reply_markup=markup)
    await Form.word.set()
    await query.message.answer("Давай тему: слово или фразу")


@dp.callback_query_handler(user_cb.filter(action='ratting'), state='*')
async def process_ratting_joke(query: types.CallbackQuery,
                               callback_data: dict,
                               ):
    markup = query.message.reply_markup
    invite_button = get_invite_button(int(callback_data['amount']))
    # remove rows with ratting
    markup['inline_keyboard'].pop(0)
    markup['inline_keyboard'].pop(0)
    # add row with invite
    markup['inline_keyboard'].insert(0, [invite_button])
    message_id = query.message.message_id
    message_text = query.message.text
    await bot.edit_message_text(text=message_text,
                                chat_id=query.from_user.id,
                                message_id=message_id,
                                reply_markup=markup)


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
