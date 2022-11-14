#!/usr/bin/env python3
import click


@click.group()
def cli():
    pass


@cli.command()
@click.option('--token', envvar="TOKEN", help='Telegram Token')
@click.option('--hook_host', envvar="HOOK_HOST")
def aiobot(token, hook_host=None):
    if not hook_host:
        from anecdoter.consts import DOMAIN
        hook_host = f'https://{DOMAIN}'
    from anecdoter.bot_app import AioBot
    aio_bot = AioBot(token=token,
                     web_hook_host=hook_host,
                     web_hook_path='/webhook',
                     web_app_host='0.0.0.0',
                     web_app_port=8443,
                     )
    aio_bot.run_aiogram()


@cli.command()
@click.option('--token_2', envvar="TOKEN_2")
def telebot(token_2):
    from anecdoter.bot_app import TeleBot
    from anecdoter.cache import cache
    tele_bot = TeleBot(token=token_2)
    try:
        tele_bot.run_telebot()
    except Exception as e:
        status = cache.drop_all_cache_to_db()
        print("TELEBOT fell\n"*10, e, 'drop to db',  status)
        tele_bot.run_telebot()


@cli.command()
def web():
    from anecdoter.web_app import create_app
    app = create_app()
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    cli()
