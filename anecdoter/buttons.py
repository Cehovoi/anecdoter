from telebot import types
from anecdoter.consts import GRADE


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