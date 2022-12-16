import telebot
import os


def get_chat_ids():
    try:
        import anecdoter
    except ModuleNotFoundError:
        print("ModuleNotFoundError!\n"*3)
        import sys
        sys.path.append(os.path.abspath(''))
    from anecdoter import create_app
    create_app().app_context().push()
    from anecdoter import db
    from anecdoter.models import User
    chat_ids = db.session.query(User.user_id).all()
    return tuple(ch_i[0] for ch_i in chat_ids)


def create_button(text='', switch_inline_query=None, url=None):

    button = telebot.types.InlineKeyboardButton(
        text,
        url=url,
        switch_inline_query=switch_inline_query,
    )
    return button


def get_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    forward_button = create_button(
        text='Рассказать другу',
        switch_inline_query='\nБот рассказывающий анекдоты 👆'
    )
    url_button = create_button(
        text='Почитать анекдоты',
        url='anecdoter.su/rating/5/1'
    )
    keyboard.row(url_button)
    keyboard.row(forward_button)
    return keyboard


def send_message():
    token = os.getenv('TOKEN')
    path = os.path.abspath(__file__)
    file_name = 'guid_notify.txt'
    file_path = path[:path.rfind('/')] + '/' + file_name
    with open(file_path, 'r') as file:
        message = file.read()
    bot = telebot.TeleBot(token)
    keyboard = get_keyboard()
    chat_ids = get_chat_ids()
    for chat_id in chat_ids:
        bot.send_message(chat_id, message, reply_markup=keyboard)


if __name__ == '__main__':
    send_message()
