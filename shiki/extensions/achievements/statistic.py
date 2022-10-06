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

import time
import lightbulb
import hikari
from shiki.utils import db, tools


cfg = tools.load_data('./settings/config')
achievements = tools.load_data('./settings/achievements')
users = db.connect().get_database('shiki').get_collection('users')
stats = db.connect().get_database('shiki').get_collection('stats')
plugin = lightbulb.Plugin("Statistic")


@plugin.listener(hikari.GuildMessageCreateEvent)
async def message_created(ctx: hikari.GuildMessageCreateEvent):
    user = ctx.author
    if user.is_bot: return
    data = db.find_document(stats, {'_id': user.id})
    if data == None: return
    data['messages_total'] += 1
    if data['messages_total'] == 1:
        tools.grant_achievement(user.id, 0)
        achievement_title = achievements['0']['title']
        achievement_desc = achievements['0']['description']
        await ctx.message.respond(f'Вы получили достижение:\n``{achievement_title} - {achievement_desc}``')
    data['messages_today'] += 1
    if data['messages_date'] == None: data['messages_date'] = time.time() // 86400
    if time.time() // 86400 - data['messages_date'] >= 1: 
        data['messages_date'] = time.time() // 86400
        data['messages_today'] = 1
    if data['messages_today'] == 100:
        if tools.grant_achievement(user.id, 1):
            achievement_title = achievements['1']['title']
            achievement_desc = achievements['1']['description']
            await ctx.message.respond(f'Вы получили достижение:\n``{achievement_title} - {achievement_desc}``')
    db.update_document(stats, {'_id': user.id}, data)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
