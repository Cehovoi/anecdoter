#!/usr/bin/env python3
import os

import click
import telebot
from anecdoter import Bot as AneBot, create_app, db
from anecdoter.consts import RATING, GRADE


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
@click.option('--host', envvar="HOST", help='host')
def web(host):
    if not host:
        host = '0.0.0.0'
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

