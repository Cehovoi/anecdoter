#!/usr/bin/env python3
import click


@click.group()
def cli():
    pass


@cli.command()
def aiobot():
    from anecdoter.aiobot_app import start_aiobot
    start_aiobot()


@cli.command()
def web():
    from anecdoter.web_app import create_app
    app = create_app()
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    cli()
