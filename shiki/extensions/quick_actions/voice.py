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
import lightbulb
import hikari
from shiki.utils import db, tools
import os


cfg = tools.load_data('./settings/config')
users = db.connect().get_database(os.environ['db']).get_collection('users')
plugin = lightbulb.Plugin("QuickVoice")


@plugin.listener(hikari.GuildMessageCreateEvent)
async def message_sent(ctx: hikari.GuildMessageCreateEvent):
    if ctx.author.is_bot: return
    if ctx.content == None: return
    raw_content = ctx.content.lower()
    if not raw_content.startswith('шики'): return
    content = tools.fetch_content(raw_content)

    reference_user = ctx.message.message_reference
    if reference_user != None:
        reference_id = ctx.message.message_reference.id
        reference_message = await ctx.get_channel().fetch_message(reference_id)
        reference_user = reference_message.author
        reference_state = ctx.get_guild().get_voice_state(reference_user)
    
    if content == 'move':
        roles = [k.id for k in ctx.member.get_roles()]
        if cfg[cfg['mode']]['roles']['admin'] not in roles and\
           cfg[cfg['mode']]['roles']['mod'] not in roles:
           return
        if reference_user == None: return
        author_state = ctx.get_guild().get_voice_state(ctx.author_id)
        if reference_state == None:
            return await ctx.message.respond('%s не в ГК <:1720kannauhh:1028186197287247874>' % reference_user.mention,
                                             reply=True)
        if author_state == None:
            return await ctx.message.respond('Ты не в ГК <:9380fuminodepression3:1027509992774975518>', reply=True)
        await reference_user.edit(voice_channel=author_state.channel_id)
        return await ctx.message.respond(
            'Переместила <:5514kannasleep:1028186236990537749>',
            reply=True
        )
    
    if content == 'move all':
        pass

    if content == 'mute all' or content == 'unmute all':
        roles = [k.id for k in ctx.member.get_roles()]
        if cfg[cfg['mode']]['roles']['admin'] not in roles and\
           cfg[cfg['mode']]['roles']['mod'] not in roles:
           return
        
        voice = ctx.get_guild().get_voice_state(ctx.author_id)
        guild = plugin.bot.cache.get_guild(ctx.guild_id)
        users = [v for v in guild.get_voice_states().values()
                if v.channel_id == voice.channel_id and v.user_id != voice.user_id]

        if content == 'mute all':
            for v in users:
                asyncio.create_task(v.member.edit(mute=True))
        else:
            for v in users:
                asyncio.create_task(v.member.edit(mute=False))


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
