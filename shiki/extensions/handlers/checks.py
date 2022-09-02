import lightbulb
import hikari
import logging
from shiki.utils import db, tools
import shiki


cfg = tools.load_file('config')
plugin = lightbulb.Plugin("HandlersChecks")


@plugin.listener(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if isinstance(event.exception, lightbulb.MissingRequiredRole):
        await event.context.respond(hikari.ResponseType.MESSAGE_UPDATE, embed=hikari.Embed(
            title='Нет ролей',
            description='Чтобы использовать эту команду вам нужно иметь специальную роль',
            color=shiki.Colors.ERROR
        ))
        return
    raise event.exception


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
