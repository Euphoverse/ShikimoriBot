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
        if reference == None:
            return await plugin.app.rest.create_message(
                ctx.channel_id,
                'Ты не указал какое сообщение закрепить <:2987zerotwo:1027903070572662834>',
                reply=True
            )

        await plugin.app.rest.pin_message(
            ctx.channel_id,
            reference.id
        )
        return await plugin.app.rest.create_message(
            ctx.channel_id,
            'Закрепила <:2530cirowo:1027509894284329032>',
            reply=True
        )

    if content == 'avatar':
        if ctx.message.message_reference == None: 
            reference = ctx.author.display_avatar_url
        else: 
            reference_id = ctx.message.message_reference.id
            reference = await ctx.get_channel().fetch_message(reference_id)
            reference = reference.author.display_avatar_url
        return await ctx.message.respond(reference, reply=True)

    if content == 'time since':
        reference = ctx.message.message_reference
        if reference == None: return
        else:
            reference = ctx.message.message_reference.id
            reference = await ctx.get_channel().fetch_message(reference)
        time_since = datetime.now(tz=timezone.utc) - reference.timestamp
        return await ctx.message.respond('Прошло `%s` <a:8618blondenekowave:1027902961520754698>' % str(time_since).split('.')[0], reply=True)

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
        return await ctx.message.respond(f'Модератором {reference.username} является {moderator} <a:7755kannasurprised:1028186246545154068>',
                                        reply=True)

    if content == 'slowmode':
        roles = [k.id for k in ctx.member.get_roles()]
        if cfg[cfg['mode']]['roles']['admin'] not in roles or\
           cfg[cfg['mode']]['roles']['mod'] not in roles:
           return
        channel = ctx.get_channel()
        number = int(re.search(r'\d+', ctx.content).group(0))
        if number > 21600:
            return await ctx.message.respond('Слишком большое значение для слоумода <:3980blondenekoscared:1027902946442223646>', reply=True)
        await channel.edit(rate_limit_per_user=int(number))
        return await ctx.message.respond(f'Установила слоумод **{number}**c <:7652_ZeroTwoUwU:1027903090940203009>', reply=True)

    if content == 'join':
        reference = ctx.message.message_reference
        if reference == None: reference = ctx.member
        else:
            reference = ctx.message.message_reference.id
            reference = await ctx.get_channel().fetch_message(reference)
            reference = ctx.get_guild().get_member(reference.author.id)
        return await ctx.message.respond(f'<t:{round(time.mktime(reference.joined_at.timetuple()))}>', reply=True)

    if content == 'online':
        online = 0
        offline = 0
        for user in await plugin.bot.rest.fetch_members(ctx.get_guild().id):
            if not user.is_bot:
                if user.get_presence() != None: online += 1
                else: offline += 1
        return await ctx.message.respond(f'Онлайн: ``{online} / {offline + online}``', reply=True)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
