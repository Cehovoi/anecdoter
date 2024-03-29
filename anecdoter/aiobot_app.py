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

from .consts import GRADE, DOMAIN, DOES_NOT_EXISTS, ONE_MORE, JOKES_OVER, \
    HELP_MESSAGE
from .contoller import get_admin_rights, RatingFill
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
    cert = os.path.abspath(f'nginx/.ssl/{os.getenv("CERT")}')
    key = os.path.abspath(f'nginx/.ssl/{os.getenv("KEY")}')
    logging.info(f'key {key}, cert {cert}')
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


def get_rating_buttons():
    buttons = [get_button(
        title=GRADE * var,
        action=f'rating',
        amount=var,
    )
        for var in range(1, 6)]
    return buttons


def get_invite_button(amount, uid):
    # bad idea get date from server
    # different users have different time
    # date = datetime.now().isoformat(sep=" ", timespec="seconds")
    invite_button = types.InlineKeyboardButton(
        text=f'{GRADE * amount}, на сайт 👆',
        callback_data=user_cb.new(action='invite', amount=0),
        url=f'{DOMAIN}/rating/{amount}/{uid}',
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
rating_buttons = get_rating_buttons()


def get_user_keyboard(joke_word, enable_rating=True):
    markup = types.InlineKeyboardMarkup()
    if enable_rating:
        markup.row(*rating_buttons[:3])
        markup.row(*rating_buttons[-2:])
    confirm_buttons = get_confirm_buttons(joke_word)
    more_button = confirm_buttons[0]
    new_joke_button = confirm_buttons[1]
    markup.row(more_button, new_joke_button)
    return markup


async def process_user_joke(state, word=None, username=None):
    try:
        user_data = await state.get_data()
        joke = next(user_data['word_f'])
        user_data['joke_index'] += 1
    except KeyError:
        # data has been pushed out, let's recreate it!
        await state.set_data(data=dict(word=word, username=username))
        # recursion
        return await process_user_joke(state)
    except StopIteration:
        user_data['page_num'] += 1
        user_data['joke_index'] = 0
        if user_data['page_num'] <= user_data['amount_pages']:
            await state.set_data(data=dict(user_data=user_data))
            # recursion
            return await process_user_joke(state)
        else:
            # jokes is over
            user_data['page_num'] = 1
            await state.set_data(data=dict(user_data=user_data))
            return
    return joke


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
    markup = types.ReplyKeyboardRemove()
    await Form.word.set()
    await message.answer("Давай тему: слово или фразу", reply_markup=markup)


@dp.message_handler(state='*', commands='help')
@dp.message_handler(Text(equals='help', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    await message.answer(HELP_MESSAGE)


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
    """
        input markup schema:
    not rated:
    0. |  *  | |  **  | |  ***   |
    1. |  ****  | |  *****  |
    2. | Ещё {word} | | Новый анекдот |
    rated:
    0. | *** {datetime.now()} на сайт |
    1. | Ещё {word} | | Новый анекдот |
    """
    chat_id = message.chat.id
    joke_word = message.text
    try:
        await state.set_data(data=dict(word=joke_word,
                                       username=message.chat.username))
    except DoesNotExists:
        return SendMessage(chat_id, DOES_NOT_EXISTS)
    joke = await process_user_joke(state)
    markup = get_user_keyboard(joke_word, enable_rating=joke != None)
    joke = joke if joke else JOKES_OVER
    await Form.next()
    return SendMessage(chat_id, joke, reply_markup=markup)


@dp.callback_query_handler(user_cb.filter(action='more'), state=Form.word)
async def process_next_word(query: types.CallbackQuery):
    await query.message.answer("Пишем ручками слово или фразу")


@dp.callback_query_handler(user_cb.filter(action='more'), state=Form.telling)
async def process_next_word(query: types.CallbackQuery, state: FSMContext):
    """
        input markup schema:
    not rated:
    0. |  *  | |  **  | |  ***   |
    1. |  ****  | |  *****  |
    2. | Ещё {word} | | Новый анекдот |
    rated:
    0. | *** {datetime.now()} на сайт |
    1. | Ещё {word} | | Новый анекдот |
    """
    markup = query.message.reply_markup
    confirm_buttons = markup['inline_keyboard'].pop()
    await bot.edit_message_text(text=query.message.text,
                                chat_id=query.from_user.id,
                                message_id=query.message.message_id,
                                reply_markup=markup)
    # needs when current user data pushed out from cache dict
    word = confirm_buttons[0]["text"][len(ONE_MORE) + 1:]
    username = query.message.chat.username
    joke = await process_user_joke(state, word, username)
    keyboard = markup['inline_keyboard']
    # if joke already rated
    if len(keyboard) <= 1 or not joke:
        # remove grade button with link to site
        keyboard = []
        if joke:
            keyboard.insert(0, rating_buttons[-2:])
            keyboard.insert(0, rating_buttons[:3])
    keyboard.append(confirm_buttons)
    markup['inline_keyboard'] = keyboard
    joke = joke if joke else JOKES_OVER
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


@dp.callback_query_handler(user_cb.filter(action='rating'), state='*')
async def process_rating_joke(query: types.CallbackQuery, callback_data: dict):
    user_id = query.from_user.id
    message_text = query.message.text
    grade = int(callback_data['amount'])
    rating = RatingFill(uid=user_id, joke=message_text, grade=grade)
    rating.update_db()
    markup = query.message.reply_markup
    invite_button = get_invite_button(grade, user_id)
    # remove rows with rating
    markup['inline_keyboard'].pop(0)
    markup['inline_keyboard'].pop(0)
    # add row with invite
    markup['inline_keyboard'].insert(0, [invite_button])
    message_id = query.message.message_id
    await bot.edit_message_text(text=message_text,
                                chat_id=user_id,
                                message_id=message_id,
                                reply_markup=markup)


@dp.errors_handler(exception=MessageNotModified)
async def message_not_modified_handler(update, error):
    # for skipping this exception
    return True


async def on_startup(dp):
    bot_commands = [
        types.BotCommand(command='/start', description='Поехали!'),
        types.BotCommand(command='/help', description='Что здесь происходит'),
        types.BotCommand(command='/admin', description='Админка для админов'),
    ]
    await bot.set_my_commands(bot_commands)
    await bot.set_webhook(
        url=web_hook_url,
        certificate=open(f'nginx/.ssl/{os.getenv("CERT")}', 'rb')
    )


async def on_shutdown(dp):
    logging.warning('Shutting down..')
    status = cache.drop_all_cache_to_db()
    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()
    logging.warning(f'{status}\nBye!')


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
