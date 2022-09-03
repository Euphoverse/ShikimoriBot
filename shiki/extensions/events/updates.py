from datetime import datetime, timezone
import logging
import lightbulb
import hikari
from shiki.utils import db, tools
import shiki
import aiohttp


cfg = tools.load_file('config')
users = db.connect().get_database('shiki').get_collection('users')
plugin = lightbulb.Plugin("EventsUpdates")
local_tz = datetime.now(timezone.utc).astimezone().tzinfo


@plugin.listener(hikari.ScheduledEventUpdateEvent)
async def update_listener(event: hikari.ScheduledEventUpdateEvent):
    e = event.event
    data = tools.load_data('events')
    if str(e.id) not in data:
        return

    if e.status == hikari.ScheduledEventStatus.ACTIVE and not data[str(e.id)]['started']:
        data[str(e.id)]['started'] = True
        async with aiohttp.ClientSession(shiki.WAIFUPICS) as s:
            async with s.get('/sfw/smile') as resp:
                if resp.status != 200:
                    image_url = None
                else:
                    image_url = (await resp.json())['url']
        embed = hikari.Embed(
            title='Ивент %s начался' % e.name,
            description='Ивент начался! Скорее [присоединяйтесь](%s) в ГК с ведущим' % data[str(
                e.id)]['link'],
            color=shiki.Colors.ANC_HIGH,
            timestamp=datetime.now(local_tz)
        )
        embed.set_footer('Автоматическое сообщение',
                         icon=plugin.bot.get_me().display_avatar_url.url)
        embed.set_image(image_url)
        await plugin.bot.rest.create_message(cfg[cfg['mode']]['channels']['announcements'], embed=embed)
        tools.update_data('events', data)
        return

    if e.status == hikari.ScheduledEventStatus.COMPLETED:
        data.pop(str(event.event.id))
        tools.update_data('events', data)
        async with aiohttp.ClientSession(shiki.WAIFUPICS) as s:
            async with s.get('/sfw/wave') as resp:
                if resp.status != 200:
                    image_url = None
                else:
                    image_url = (await resp.json())['url']
        embed = hikari.Embed(
            title='Ивент %s завершён' % e.name,
            description='Спасибо всем за игру! Вы можете оставить свой отзыв об ивенте в [специальной форме](https://forms.gle/bVt1NDJTJYUm9n5V8)',
            color=shiki.Colors.ANC_LOW,
            timestamp=datetime.now(local_tz)
        )
        embed.set_footer('Автоматическое сообщение',
                         icon=plugin.bot.get_me().display_avatar_url.url)
        embed.set_image(image_url)
        await plugin.bot.rest.create_message(cfg[cfg['mode']]['channels']['announcements'], embed=embed)
        tools.update_data('events', data)
        return

    data[str(e.id)]['date'] = e.start_time.strftime(cfg['time_format'])
    data[str(e.id)]['title'] = e.name

    tools.update_data('events', data)

    await plugin.bot.rest.create_message(cfg[cfg['mode']]['channels']['mods_only'], embed=hikari.Embed(
        title='Ивент обновлён',
        description='Ивент %s обновлён. Время начала: %s' % (
            e.name, data[str(e.id)]['date']),
        color=shiki.Colors.WARNING,
        timestamp=datetime.now(local_tz)
    ))


@plugin.listener(hikari.ScheduledEventDeleteEvent)
async def delete_listener(event: hikari.ScheduledEventDeleteEvent):
    data = tools.load_data('events')
    data.pop(str(event.event.id))
    tools.update_data('events', data)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
