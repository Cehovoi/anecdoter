#!/usr/bin/env python3
import os

import click
import telebot
from anecdoter import Bot as AneBot, create_app, db
from anecdoter.consts import RATING, GRADE


def button(value):
    return telebot.types.KeyboardButton(value)


def collect_buttons(content, sequence):
    return tuple(button(content * i) for i in sequence)


def add_rating_button():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    grade_buttons = collect_buttons(GRADE, range(1, 6))
    markup.row(*grade_buttons[:3])
    markup.row(*grade_buttons[-2:])
    markup.row(*collect_buttons(1, ('ДА', 'НЕТ')))
    return markup


def add_confirm_button():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*collect_buttons(1, ('ДА', 'НЕТ')))
    return markup


@click.group()
def cli():
    pass


@cli.command()
@click.option('--token', envvar="TOKEN", help='Telegram Token')
def bot(token):
    bot = telebot.TeleBot(token, parse_mode=None)
    ane_bot = AneBot()
    offset = None
    rating_buttons = add_rating_button()
    confirm_buttons = add_confirm_button()
    while True:
        for message in bot.get_updates(offset=offset):
            try:
                offset = message.update_id + 1
                response = ane_bot.handle(message.message.chat.id,
                                          message.message.text)
                if response.endswith(RATING):
                    markup = rating_buttons
                elif response.endswith('?'):
                    markup = confirm_buttons
                else:
                    markup = None
                bot.send_message(message.message.chat.id, response,
                                 reply_markup=markup)
            except Exception as e:
                pass


app = create_app()


@cli.command()
@click.option('--host', envvar="HOST", help='host')
def web(host):
    if not host:
        host = '0.0.0.0'
    app.secret_key = 'super secret key'
    app.run(host=host)


@cli.command("create_db")
def create_db():
    with app.app_context():
        from anecdoter import db
        print("db", db)
        db.drop_all()
        db.create_all()
        db.session.commit()


if __name__ == '__main__':
    cli()

