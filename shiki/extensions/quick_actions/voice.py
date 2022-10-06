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

import lightbulb
import hikari
from shiki.utils import db, tools


cfg = tools.load_data('./settings/config')
users = db.connect().get_database('shiki').get_collection('users')
plugin = lightbulb.Plugin("QuickVoice")


@plugin.listener(hikari.GuildMessageCreateEvent)
async def message_sent(ctx: hikari.GuildMessageCreateEvent):
    if ctx.author.is_bot: return
    raw_content = ctx.content.lower()
    if not raw_content.startswith('шики'): return
    content = tools.fetch_content(raw_content)

    if content == 'move':
        roles = [k.id for k in ctx.member.get_roles()]
        if cfg[cfg['mode']]['roles']['admin'] not in roles or\
           cfg[cfg['mode']]['roles']['mod'] not in roles:
           return
        reference = ctx.message.message_reference
        if reference == None: return
        else:
            reference = ctx.message.message_reference.id
            reference = await ctx.get_channel().fetch_message(reference)
            reference = ctx.get_guild().get_member(reference.author)
        reference_state = ctx.get_guild().get_voice_state(reference.id)
        user_state = ctx.get_guild().get_voice_state(ctx.author_id)
        if reference_state == None:
            return await ctx.message.respond('Этого пользователя нет в голосовых каналах')
        if user_state == None:
            return await ctx.message.respond('Вы должны быть в голосовом канале для этого действия')
        await reference.edit(voice_channel=user_state.channel_id)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
