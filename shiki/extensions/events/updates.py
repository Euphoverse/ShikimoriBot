from datetime import datetime, timedelta
import logging
import lightbulb
import hikari
from shiki.utils import db, tools
import shiki


cfg = tools.load_file('config')
users = db.connect().get_database('shiki').get_collection('users')
plugin = lightbulb.Plugin("EventsUpdates")


@plugin.listener(hikari.ScheduledEventUpdateEvent)
async def update_listener(event: hikari.ScheduledEventUpdateEvent):
    e = event.event
    data = tools.load_data('events')
    if str(e.id) not in data:
        return

    data[str(e.id)]['date'] = e.start_time.strftime(cfg['time_format'])
    data[str(e.id)]['title'] = e.name

    tools.update_data('events', data)

    await plugin.bot.rest.create_message(cfg[cfg['mode']]['channels']['mods_only'], embed=hikari.Embed(
        title='Ивент обновлён',
        description='Ивент %s обновлён. Время начала: %s' % (
            e.name, data[str(e.id)]['date']),
        color=shiki.Colors.WARNING
    ))


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
