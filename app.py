#!/usr/bin/env python3
import os

import click
import telebot
from flask import request
from anecdoter import Bot as AneBot, create_app, db

from anecdoter.buttons import add_buttons
from anecdoter.consts import RATING, GRADE


def aaa_bu():
    markup = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton('Админка',
                                                callback_data='unseen')
    markup.add(button)
    return markup

#
# @blue.route('/webhook', methods=['POST'])
# def webhook():
#     if request.headers.get('content-type') == 'application/json':
#         return request.get_data().decode('utf-8')


@click.group()
def cli():
    pass


# @cli.command()
# @click.option('--token', envvar="TOKEN", help='Telegram Token')
# @click.option('--admin_id', envvar="ADMIN_ID",)
# def bot(token, admin_id='0'):
#     t_ane_bot = telebot.TeleBot(token, parse_mode=None)
#     # to use callback in admin buttons
#     # globals()['t_ane_bot'] = t_ane_bot
#     ane_bot = AneBot()
#     grades_confirm = add_buttons(all_buttons=True)
#     confirm = add_buttons(all_buttons=False)
#     admin_grades_confirm = add_buttons(all_buttons=True, admin_button=True)
#     admin_confirm = add_buttons(all_buttons=False, admin_button=True)
#     offset = None
#     # param comes as str
#     admin_id = int(admin_id)
#     while True:
#         for message in t_ane_bot.get_updates(offset=offset):
#             chat_id = message.message.chat.id
#             admin = admin_id == chat_id
#             try:
#                 offset = message.update_id + 1
#                 response = ane_bot.handle(chat_id, message.message.text)
#                 if admin:
#                     grades_confirm = admin_grades_confirm
#                     confirm = admin_confirm
#                 if response.endswith(RATING):
#                     markup = grades_confirm
#                 elif response.endswith('?') or admin:
#                     markup = confirm
#                 else:
#                     markup = None
#                 t_ane_bot.send_message(chat_id, response, reply_markup=markup)
#             except Exception as e:
#                 print('Bot crashed, error - ', e)
#                 ane_bot.storage.drop_all_cache_to_db()
#                 # restart bot
#                 bot(token)

@cli.command()
@click.option('--token', envvar="TOKEN", help='Telegram Token')
@click.option('--admin_id', envvar="ADMIN_ID",)
def bot(token, admin_id='0'):
    from anecdoter.aiobot import AioBot
    from anecdoter.aiobot import add_buttons
    buttons = {'grades_confirm': add_buttons(all_buttons=True),
               'confirm': add_buttons(all_buttons=False),
               }
    b = AioBot(token=token,
               admin_id=int(admin_id),
               web_hook_host='https://4e8b-176-53-210-25.eu.ngrok.io',
               web_hook_path='/',
               web_app_host='localhost',
               web_app_port=8444,
               buttons=buttons,
               )
    b.run_aiogram()







app = create_app()


@cli.command()
@click.option('--host', envvar="HOST", help='host')
def web(host):
    if not host:
        host = '0.0.0.0'
    app.run(host=host, port='8444')


@cli.command("create_db")
def create_db():
    with app.app_context():
        from anecdoter import db
        print("db", db)
        db.drop_all()
        db.create_all()
        db.session.commit()


# @cli.command()
# @click.option('--token', envvar="TOKEN", help='Telegram Token')
# @click.option('--admin_id', envvar="ADMIN_ID", help='admin chat id')
# def bot(token, admin_id='0'):
#     from anecdoter.bot import TeleConnector
#
#     # teleconnector = TeleConnector(token=token, admin_id=admin_id)
#     # print("teleconnector", teleconnector)
#     # teleconnector.run()
#     # create class attributes
#     WEB_HOOK_URL = 'https://4572-176-53-210-25.eu.ngrok.io'
#     TeleConnector.connector = telebot.TeleBot(token, parse_mode=None)
#     # TeleConnector.connector.remove_webhook()
#     # import time
#     # time.sleep(1)
#     # TeleConnector.connector.set_webhook(url=WEB_HOOK_URL)
#     TeleConnector.admin_id = int(admin_id)
#     from anecdoter.views import webhook_runner
#     webhook_runner()
#     #TeleConnector.run()


if __name__ == '__main__':
    cli()

