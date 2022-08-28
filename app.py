#!/usr/bin/env python3
import click
import telebot
from ane_searcher_bot import Bot as AneBot, create_app
from ane_searcher_bot.consts import RATING, GRADE


@click.group()
def cli():
    pass


def add_rating_button():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton(GRADE)
    btn2 = telebot.types.KeyboardButton(GRADE*2)
    btn3 = telebot.types.KeyboardButton(GRADE*3)
    btn4 = telebot.types.KeyboardButton(GRADE*4)
    btn5 = telebot.types.KeyboardButton(GRADE*5)
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup


def add_confirm_button():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('ДА')
    btn2 = telebot.types.KeyboardButton('НЕТ')
    markup.add(btn1, btn2)
    return markup


@cli.command()
@click.option('--token', envvar="TOKEN", help='Telegram Token')
def bot(token):
    bot = telebot.TeleBot(token, parse_mode=None)
    ane_bot = AneBot()
    offset = None
    while True:
        for message in bot.get_updates(offset=offset):
            try:
                offset = message.update_id + 1
                response = ane_bot.handle(message.message.chat.id,
                                          message.message.text)
                if response.endswith(RATING):
                    markup = add_rating_button()
                elif response.endswith('?'):
                    markup = add_confirm_button()
                else:
                    markup = None
                bot.send_message(message.message.chat.id, response,
                                 reply_markup=markup)
            except Exception as e:
                pass


app = create_app()


@cli.command()
def web():
    app.run(debug=True)


if __name__ == '__main__':
    cli()

