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

from datetime import datetime
import lightbulb
import hikari
from shiki.utils import db, tools, embeds


cfg = tools.load_data('./settings/config')
stats = db.connect().get_database('shiki').get_collection('stats')
plugin = lightbulb.Plugin("QuickStats")
emoji_denied = cfg['emojis']['access_denied']


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
    
    if content == 'messages_total':
        if reference_user == None:
            user = ctx.author
        else: 
            user = reference_user
        data = db.find_document(stats, {'_id': user.id})
        if data == None:
            return ctx.message.respond(embeds.user_not_found())
        return await ctx.message.respond(f'{user.username} отправил {data["messages_total"]} сообщений за всё время!')
    
    if content == 'messages_today':
        if reference_user == None:
            user = ctx.author
        else: 
            user = reference_user
        data = db.find_document(stats, {'_id': user.id})
        if data == None:
            return ctx.message.respond(embeds.user_not_found())
        return await ctx.message.respond(f'{user.username} отправил {data["messages_today"]} сообщений за сегодня!')

    if content == 'vc_hours':
        if reference_user == None:
            user = ctx.author
        else: 
            user = reference_user
        data = db.find_document(stats, {'_id': user.id})
        if data == None:
            return ctx.message.respond(embeds.user_not_found())
        vc_time = data["time_in_vc"]
        hh = round(vc_time // 3600)
        mm = round((vc_time // 60) % 60)
        ss = round(vc_time % 60)
        if(mm < 10): mm = f'0{mm}'
        if(ss < 10): ss = f'0{ss}'
        return await ctx.message.respond(f'{user.username} просидел ``{hh}:{mm}:{ss}`` в голосовых каналах!')


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
