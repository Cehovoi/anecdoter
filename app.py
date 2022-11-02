#!/usr/bin/env python3
import click


@click.group()
def cli():
    pass


@cli.command()
@click.option('--token', envvar="TOKEN", help='Telegram Token')
@click.option('--hook_host', envvar="HOOK_HOST")
def aiobot(token, hook_host):
    from anecdoter.bot_app import AneBot
    from anecdoter.bot_app import add_buttons
    buttons = {'grades_confirm': add_buttons(all_buttons=True),
               'confirm': add_buttons(all_buttons=False),
               }
    aio_bot = AneBot(token=token,
                     web_hook_host=hook_host,
                     web_hook_path='/',
                     web_app_host='0.0.0.0',
                     web_app_port=8444,
                     buttons=buttons,
                     )
    aio_bot.run_aiogram()


@cli.command()
@click.option('--token_2', envvar="TOKEN_2")
def telebot(token_2):
    print("token\n"*10, token_2)
    from anecdoter.bot_app import AneBot
    from anecdoter.bot_app import add_buttons
    buttons = {'grades_confirm': add_buttons(all_buttons=True),
               'confirm': add_buttons(all_buttons=False),
               }
    tele_bot = AneBot(token=token_2, buttons=buttons)
    tele_bot.run_telebot()


@cli.command()
def web():
    from anecdoter.web_app import create_app
    app = create_app()
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    cli()
