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
import time
import lightbulb
import hikari
from shiki.utils import db, tools
import string


cfg = tools.load_data('./settings/config')
achievements = tools.load_data('./settings/achievements')
users = db.connect().get_database('shiki').get_collection('users')
stats = db.connect().get_database('shiki').get_collection('stats')
plugin = lightbulb.Plugin("AchieveStatistic")

vc_tmp = {}


@plugin.listener(hikari.GuildMessageCreateEvent)
async def message_created(ctx: hikari.GuildMessageCreateEvent):
    user = ctx.author
    if user.is_bot:
        return

    data = db.find_document(stats, {'_id': user.id})
    if data == None:
        return

    data['messages_total'] += 1
    if data['messages_total'] == 1:
        await tools.grant_achievement(user, '0')

    data['messages_today'] += 1
    if data['messages_date'] == None:
        data['messages_date'] = time.time() // 86400
    if time.time() // 86400 - data['messages_date'] >= 1:
        data['messages_date'] = time.time() // 86400
        data['messages_today'] = 1
    if data['messages_today'] == 100:
        await tools.grant_achievement(user, '1')

    if ctx.content != None:
        for s in string.ascii_lowercase:
            if s in ctx.content:
                await tools.grant_achievement(user, '2')
                break

    time_since_join = datetime.now(tz=timezone.utc) - ctx.member.joined_at
    if time_since_join.days >= 3:
        asyncio.create_task(tools.grant_achievement(user, '49'))

    db.update_document(stats, {'_id': user.id}, data)


@plugin.listener(hikari.VoiceStateUpdateEvent)
async def state_update(event: hikari.VoiceStateUpdateEvent):
    if event.state.guild_id != cfg[cfg['mode']]['guild']:
        return
    if event.state.channel_id is not None:
        await tools.grant_achievement(event.state.user_id, '3', plugin.bot.rest)

    state = event.state
    if state.user_id not in vc_tmp:
        vc_tmp[state.user_id] = datetime.now()
        return
    
    if state.channel_id is None:
        data = db.find_document(stats, {'_id': state.user_id})
        if data is None: return
        tm: timedelta
        if data['time_in_vc'] is None:
            tm = datetime.now() - vc_tmp.pop(state.user_id)
        else:
            tm = timedelta(seconds=data['time_in_vc']) + (datetime.now() - vc_tmp.pop(state.user_id))
        
        db.update_document(stats, {'_id': state.user_id}, {'time_in_vc': tm.total_seconds()})

        s = tm.total_seconds()
        if s > 600:
            await tools.grant_achievement(state.user_id, 
                                    '5', plugin.app.rest)

        if s > 7200:
            await tools.grant_achievement(state.user_id, 
                                    '6', plugin.app.rest)

        if s > 43_200:
            await tools.grant_achievement(state.user_id, 
                                    '7', plugin.app.rest)

        if s > 86_400:
            await tools.grant_achievement(state.user_id, 
                                    '8', plugin.app.rest)

        if s > 3_240_000:
            await tools.grant_achievement(state.user_id, 
                                    '9', plugin.app.rest)

    if state.channel_id == cfg[cfg['mode']]['channels']['radio']:
        await tools.grant_achievement(event.state.user_id, '35', plugin.bot.rest)
    
    data = tools.load_data('./data/events')
    if state.channel_id in [e['channel'] for e in data.values() if e['started'] == True]:
        await tools.grant_achievement(event.state.user_id, '43', plugin.bot.rest)
    
    if state.is_streaming == True:
        await tools.grant_achievement(event.state.user_id, '36', plugin.bot.rest)

    if state.is_video_enabled == True:
        await tools.grant_achievement(event.state.user_id, '10', plugin.bot.rest)
    
    if event.old_state != None and event.old_state.is_suppressed == True and state.is_suppressed == False:
        await tools.grant_achievement(event.state.user_id, '45', plugin.bot.rest)
    



@plugin.listener(hikari.StoppingEvent)
async def stopping(event: hikari.StoppingEvent):
    now = datetime.now()
    if vc_tmp is None: return
    for u in vc_tmp:
        tm = db.find_document(stats, {'_id': u})['time_in_vc']
        if tm is None:
            tm = timedelta(seconds=0)
        else:
            tm = timedelta(
                seconds=tm
            )

        db.update_document(stats, {'_id': u}, {
            'time_in_vc': (tm + now - vc_tmp[u]).total_seconds()
        })


@plugin.listener(hikari.ShardReadyEvent)
async def ready(event: hikari.ShardReadyEvent):
    guild = await plugin.bot.rest.fetch_guild(cfg[cfg['mode']]['guild'])
    for u in guild.get_voice_states():
        vc_tmp[u] = datetime.now()


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
