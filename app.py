#!/usr/bin/env python3
import os

import click
import telebot
from flask import request
from anecdoter import Bot as AneBot, create_app, db
from anecdoter.blue_app import blue
from anecdoter.buttons import add_buttons
from anecdoter.consts import RATING, GRADE


# def button(value):
#     return telebot.types.KeyboardButton(value)
#
#
# def collect_buttons(content, sequence):
#     return tuple(button(content * i) for i in sequence)
#
#
# def add_buttons(all_buttons=False, admin_button=False):
#     markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
#     if all_buttons:
#         grade_buttons = collect_buttons(GRADE, range(1, 6))
#         markup.row(*grade_buttons[:3])
#         markup.row(*grade_buttons[-2:])
#     markup.row(*collect_buttons(1, ('ДА', 'НЕТ')))
#     if admin_button:
#         markup.row(button('Админка'))
#     return markup


def aaa_bu():
    markup = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton('Админка',
                                                callback_data='unseen')
    markup.add(button)
    return markup



# @blue.route('/webhook', methods=['POST'])
# def webhook():
#     if request.headers.get('content-type') == 'application/json':
#         return request.get_data().decode('utf-8')


@click.group()
def cli():
    pass



@cli.command()
@click.option('--token', envvar="TOKEN", help='Telegram Token')
@click.option('--admin_id', envvar="ADMIN_ID",)
def bot(token, admin_id='0'):
    tele_bot = telebot.TeleBot(token, parse_mode=None)
    ane_bot = AneBot()
    grades_confirm = add_buttons(all_buttons=True)
    confirm = add_buttons(all_buttons=False)
    admin_grades_confirm = add_buttons(all_buttons=True, admin_button=True)
    admin_confirm = add_buttons(all_buttons=False, admin_button=True)
    offset = None
    # param comes as str
    admin_id = int(admin_id)
    while True:
        for message in tele_bot.get_updates(offset=offset):
            chat_id = message.message.chat.id
            admin = admin_id == chat_id
            try:
                offset = message.update_id + 1
                response = ane_bot.handle(chat_id, message.message.text)
                if admin:
                    grades_confirm = admin_grades_confirm
                    confirm = admin_confirm
                if response.endswith(RATING):
                    markup = grades_confirm
                elif response.endswith('?') or admin:
                    markup = confirm
                else:
                    markup = None
                tele_bot.send_message(chat_id, response, reply_markup=markup)
            except Exception as e:
                print('Bot crashed, error - ', e)
                ane_bot.storage.drop_all_cache_to_db()
                # restart bot
                bot(token)


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

