# Copyright (c) 2022, JustLian
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import asyncio
from datetime import datetime, timedelta, timezone
import logging
import zoneinfo
import lightbulb
import hikari
from shiki.utils import db, tools
import shiki
import aiohttp
import os


cfg = tools.load_data('./settings/config')
users = db.connect().get_database(os.environ['db']).get_collection('users')
plugin = lightbulb.Plugin("EventsUpdates")
local_tz = datetime.now(timezone.utc).astimezone().tzinfo


@plugin.listener(hikari.ScheduledEventUpdateEvent)
async def update_listener(event: hikari.ScheduledEventUpdateEvent):
    e = event.event
    data = tools.load_data('./data/events')
    if str(e.id) not in data:
        return

    if e.status == hikari.ScheduledEventStatus.ACTIVE and not data[str(e.id)]['started']:
        await plugin.bot.update_voice_state(e.guild_id, data[str(e.id)]['channel'])
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
        await plugin.bot.rest.create_message(cfg[cfg['mode']]['channels']['announcements'], '@everyone', embed=embed, mentions_everyone=True, role_mentions=True)
        tools.update_data('./data/events', data)
        return

    if e.status == hikari.ScheduledEventStatus.COMPLETED:
        host = await event.app.rest.fetch_user(data[str(e.id)]['host'])
        await tools.grant_achievement(host, '41')
        await plugin.bot.update_voice_state(e.guild_id, None)
        data.pop(str(event.event.id))
        tools.update_data('./data/events', data)
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
        tools.update_data('./data/events', data)
        return

    data[str(e.id)]['date'] = e.start_time.astimezone(zoneinfo.ZoneInfo('Europe/Moscow')).replace(
        second=0, microsecond=0).strftime(cfg['time_format'])
    data[str(e.id)]['title'] = e.name

    tools.update_data('./data/events', data)

    await plugin.bot.rest.create_message(cfg[cfg['mode']]['channels']['mods_only'], embed=hikari.Embed(
        title='Ивент обновлён',
        description='Ивент %s обновлён. Время начала: %s' % (
            e.name, data[str(e.id)]['date']),
        color=shiki.Colors.WARNING,
        timestamp=datetime.now(local_tz)
    ))


@plugin.listener(hikari.ScheduledEventDeleteEvent)
async def delete_listener(event: hikari.ScheduledEventDeleteEvent):
    data = tools.load_data('./data/events')
    data.pop(str(event.event.id))
    tools.update_data('./data/events', data)


@plugin.listener(hikari.ShardReadyEvent)
async def start_loop(_):
    plugin.bot.create_task(event_reminders())


async def event_reminders() -> None:
    while plugin.bot.is_alive:
        data = tools.load_data('./data/events')
        now = datetime.now().astimezone(zoneinfo.ZoneInfo(
            'Europe/Moscow')).replace(second=0, microsecond=0, tzinfo=None)
        for id in data:
            date = datetime.strptime(data[id]['date'], cfg['time_format'])

            # 10 minutes
            if now == date - timedelta(minutes=10):
                await plugin.bot.rest.create_message(
                    cfg[cfg['mode']]['channels']['mods_only'],
                    '<@%s>, ивент %s начнётся через 10 минут' % (
                        data[id]['host'], data[id]['title'])
                )

            # 5 minutes
            elif now == date - timedelta(minutes=5):
                # mods-only
                await plugin.bot.rest.create_message(
                    cfg[cfg['mode']]['channels']['mods_only'],
                    '<@%s>, ивент %s начнётся через 5 минут' % (
                        data[id]['host'], data[id]['title']),
                    user_mentions=True
                )

                # announcements
                async with aiohttp.ClientSession(shiki.WAIFUPICS) as s:
                    async with s.get('/sfw/smile') as resp:
                        if resp.status != 200:
                            image_url = None
                        else:
                            image_url = (await resp.json())['url']
                embed = hikari.Embed(
                    title='Ивент %s скоро начнётся' % data[id]['title'],
                    description='Ивент начнётся через 5 минут! [Информация](%s)' % data[
                        id]['link'],
                    color=shiki.Colors.ANC_LOW,
                    timestamp=datetime.now(local_tz)
                )
                embed.set_footer('Автоматическое сообщение',
                                 icon=plugin.bot.get_me().display_avatar_url.url)
                embed.set_image(image_url)
                await plugin.bot.rest.create_message(cfg[cfg['mode']]['channels']['announcements'], '@everyone', embed=embed, mentions_everyone=True)

        await asyncio.sleep(60)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
