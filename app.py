#!/usr/bin/env python3
import click


@click.group()
def cli():
    pass


@cli.command()
def aiobot():
    from anecdoter.aiobot_app_out import start_aiobot
    start_aiobot()


@cli.command()
@click.option('--token_2', envvar="TOKEN_2")
def telebot(token_2):
    from anecdoter.bot_app import TeleBot
    tele_bot = TeleBot(token=token_2)
    tele_bot.run_telebot()


@cli.command()
def web():
    from anecdoter.web_app import create_app
    app = create_app()
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    cli()
