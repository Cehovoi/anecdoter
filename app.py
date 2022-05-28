#!/usr/bin/env python3
import click
import telebot
from ane_searcher_bot import Bot as AneBot


# Anecdoter
# anecdot_searcher_bot
# run with this
# TOKEN='5421705848:AAEU3KtJpVKUM07Mi3AT_iwoEd4LMJuR260' python app.py
@click.command()
@click.option('--token', envvar="TOKEN", help='Telegram Token')
def main(token):
    bot = telebot.TeleBot(token, parse_mode=None)
    ane_bot = AneBot()
    offset = None
    while True:
        for message in bot.get_updates(offset=offset):
            try:
                offset = message.update_id + 1
                response = ane_bot.handle(message.message.chat.id, message.message.text)
                print(response)
                bot.send_message(message.message.chat.id, response)
            except Exception as e:
                pass

if __name__ == '__main__':
    main()
