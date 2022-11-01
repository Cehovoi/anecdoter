#!/usr/bin/env python3
import click


@click.group()
def cli():
    pass


@cli.command()
@click.option('--token', envvar="TOKEN", help='Telegram Token')
@click.option('--admin_id', envvar="ADMIN_ID")
@click.option('--hook_host', envvar="HOOK_HOST")
def bot(token, hook_host, admin_id='0', ):
    from anecdoter.bot_app import AioBot
    from anecdoter.bot_app import add_buttons
    buttons = {'grades_confirm': add_buttons(all_buttons=True),
               'confirm': add_buttons(all_buttons=False),
               }
    aiobot = AioBot(token=token,
                    admin_id=int(admin_id),
                    web_hook_host=hook_host,
                    web_hook_path='/',
                    web_app_host='0.0.0.0',
                    web_app_port=8444,
                    buttons=buttons,
                    )
    aiobot.run_aiogram()


@cli.command()
def web():
    from anecdoter.web_app import create_app
    app = create_app()
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    cli()
