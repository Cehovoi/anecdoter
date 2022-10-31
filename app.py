#!/usr/bin/env python3
import click


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
    from anecdoter.bot_app import AioBot
    from anecdoter.bot_app import add_buttons
    buttons = {'grades_confirm': add_buttons(all_buttons=True),
               'confirm': add_buttons(all_buttons=False),
               }
    aiobot = AioBot(token=token,
               admin_id=int(admin_id),
               web_hook_host='https://3d58-176-53-210-25.eu.ngrok.io',
               web_hook_path='/',
               web_app_host='localhost',
               web_app_port=8444,
               buttons=buttons,
               )
    aiobot.run_aiogram()



@cli.command()
@click.option('--host', envvar="HOST", help='host')
def web(host):
    from anecdoter.web_app import create_app
    app = create_app()
    if not host:
        host = '0.0.0.0'
    app.run(host=host)


# @cli.command("create_db")
# def create_db():
#     with app.app_context():
#         from anecdoter import db
#         print("db", db)
#         db.drop_all()
#         db.create_all()
#         db.session.commit()




if __name__ == '__main__':
    cli()

