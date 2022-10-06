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

from datetime import datetime, timezone
import time
import lightbulb
import hikari
import re
from shiki.utils import db, tools


cfg = tools.load_data('./settings/config')
users = db.connect().get_database('shiki').get_collection('users')
plugin = lightbulb.Plugin("QuickChat")


@plugin.listener(hikari.GuildMessageCreateEvent)
async def message_sent(ctx: hikari.GuildMessageCreateEvent):
    if ctx.author.is_bot: return
    raw_content = ctx.content.lower()
    if not raw_content.startswith('шики'): return
    content = tools.fetch_content(raw_content)

    if content == 'pin': 
        roles = [k.id for k in ctx.member.get_roles()]
        if cfg[cfg['mode']]['roles']['admin'] not in roles or\
           cfg[cfg['mode']]['roles']['mod'] not in roles:
           return
        reference = ctx.message.message_reference
        if reference == None: return
        return await ctx.get_channel().pin_message(reference.id)

    if content == 'avatar':
        if ctx.message.message_reference == None: reference = ctx.author.display_avatar_url
        else: 
            reference_id = ctx.message.message_reference.id
            reference = await ctx.get_channel().fetch_message(reference_id)
            reference = reference.author.display_avatar_url
        return await ctx.message.respond(reference)

    if content == 'time since':
        reference = ctx.message.message_reference
        if reference == None: return
        else:
            reference = ctx.message.message_reference.id
            reference = await ctx.get_channel().fetch_message(reference)
        time_since = datetime.now(tz=timezone.utc) - reference.timestamp
        total_seconds = round(time_since.total_seconds())
        seconds = total_seconds % 60
        minutes = total_seconds // 60 % 60
        hours = total_seconds // 3600
        if seconds == 0: seconds = ''
        else: seconds = f' ``{seconds} секунд{suff(seconds)}``'
        if minutes == 0: minutes = ''
        else: minutes = f' ``{minutes} минут{suff(minutes)}``'
        if hours == 0: hours = ''
        else: hours = f' ``{hours} час{suff(hours, hours=True)}``'
        return await ctx.message.respond(f'Прошло{hours}{minutes}{seconds}')

    if content == 'mod':
        reference = ctx.message.message_reference
        if reference == None: reference = ctx.author
        else:
            reference = ctx.message.message_reference.id
            reference = await ctx.get_channel().fetch_message(reference)
            reference = reference.author
        data = db.find_document(users, {'_id': reference.id})
        if data == None or data['mod'] == None: moderator = 'никто'
        else: moderator = ctx.get_guild().get_member(data['mod'])
        return await ctx.message.respond(f'Модератором {reference.username} является {moderator}')

    if content == 'slowmode':
        roles = [k.id for k in ctx.member.get_roles()]
        if cfg[cfg['mode']]['roles']['admin'] not in roles or\
           cfg[cfg['mode']]['roles']['mod'] not in roles:
           return
        channel = ctx.get_channel()
        number = int(re.search(r'\d+', ctx.content).group(0))
        if number > 21600: return await ctx.message.respond('Слишком большое значение для слоумода')
        await channel.edit(rate_limit_per_user=int(number))
        return await ctx.message.respond(f'Установлен слоумод **{number}**c')

    if content == 'join':
        reference = ctx.message.message_reference
        if reference == None: reference = ctx.member
        else:
            reference = ctx.message.message_reference.id
            reference = await ctx.get_channel().fetch_message(reference)
            reference = ctx.get_guild().get_member(reference.author.id)
        return await ctx.message.respond(f'<t:{round(time.mktime(reference.joined_at.timetuple()))}>')

    if content == 'online':
        online = 0
        offline = 0
        for user in await plugin.bot.rest.fetch_members(ctx.get_guild().id):
            if not user.is_bot:
                if user.get_presence() != None: online += 1
                else: offline += 1
        return await ctx.message.respond(f'Онлайн: ``{online} / {offline + online}``')


def suff(int, hours=False):
    if hours:
        suffix = 'ов'
        if int not in [11, 12, 13, 14]:
            if int % 10 > 1 and int % 10 < 5: suffix = 'а'
            elif int % 10 == 1: suffix = ''
    else:
        suffix = ''
        if int not in [11, 12, 13, 14]:
            if int % 10 == 1: suffix = 'а'
            if int % 10 > 1 and int % 10 < 5: suffix = 'ы'
    return suffix


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
