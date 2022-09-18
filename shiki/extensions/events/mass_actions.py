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
import logging
import lightbulb
import hikari
from shiki.utils import db, tools
import shiki


cfg = tools.load_data('./settings/config')
users = db.connect().get_database('shiki').get_collection('users')
plugin = lightbulb.Plugin("EventsMassActions")


@plugin.command
@lightbulb.command('forcejoin', 'forcejoin')
@lightbulb.implements(lightbulb.SlashCommand)
async def fj(ctx: lightbulb.SlashContext):
    await plugin.bot.update_voice_state(ctx.guild_id, ctx.get_guild().get_voice_state(ctx.user).channel_id)


@plugin.listener(hikari.VoiceStateUpdateEvent)
async def member_update(event: hikari.VoiceStateUpdateEvent):
    if event.state.member.id != plugin.bot.get_me().id:
        return
    voice = event.state

    try:
        host = [e for e in tools.load_data('./data/events').values()
                if e['started']][0]['host']
    except IndexError:
        host = 0

    guild = plugin.bot.cache.get_guild(event.guild_id)
    users = [v for v in guild.get_voice_states().values()
             if v.channel_id == voice.channel_id and v.user_id not in [voice.user_id, host]]

    if voice.is_guild_muted:
        for v in users:
            asyncio.create_task(v.member.edit(mute=True))
    else:
        for v in users:
            asyncio.create_task(v.member.edit(mute=False))

    if voice.is_guild_deafened:
        for v in users:
            asyncio.create_task(v.member.edit(deaf=True))
    else:
        for v in users:
            asyncio.create_task(v.member.edit(deaf=False))


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
