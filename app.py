#!/usr/bin/env python3
import os
import click
import telebot
from ane_searcher_bot import Bot as AneBot, create_app
from flask.cli import FlaskGroup

@click.group()
def cli():
    pass


def add_button():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("★")
    btn2 = telebot.types.KeyboardButton("★★")
    btn3 = telebot.types.KeyboardButton("★★★")
    btn4 = telebot.types.KeyboardButton("★★★★")
    btn5 = telebot.types.KeyboardButton("★★★★★")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup
# Anecdoter
# anecdot_searcher_bot
# run with this
# TOKEN='5421705848:AAEU3KtJpVKUM07Mi3AT_iwoEd4LMJuR260' python app.py
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
                print('response', response, 'response')

                # btn1 = telebot.types.KeyboardButton("👋 Поздороваться")
                # btn2 = telebot.types.KeyboardButton("❓ Задать вопрос")
                if response.endswith('(не забудь оценить этот)?'):
                    markup = add_button()
                else:
                    markup = None
                bot.send_message(message.message.chat.id, response,
                                 reply_markup=markup)
                #bot.send_message(message.message.chat.id, response)
            except Exception as e:
                pass

app = create_app()

@cli.command()
def web():
    app.run(debug=True)


if __name__ == '__main__':
    cli()
    # app = create_app()
    #app.run(debug=True)
    #main()
