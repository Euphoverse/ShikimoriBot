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


cfg = tools.load_data('./settings/config')
achievements = tools.load_data('./settings/achievements')
users = db.connect().get_database('shiki').get_collection('users')
stats = db.connect().get_database('shiki').get_collection('stats')
plugin = lightbulb.Plugin("AchievePresence")


@plugin.listener(hikari.PresenceUpdateEvent)
async def update(ctx: hikari.PresenceUpdateEvent):
    if ctx.guild_id != cfg[cfg['mode']]['guild']: return
    user = await ctx.fetch_user()
    if user.is_bot: return
    await activity_check(ctx.presence, user)


@plugin.listener(hikari.ShardReadyEvent)
async def ready(ctx: hikari.ShardReadyEvent):
    members = await plugin.bot.rest.fetch_members(cfg[cfg['mode']]['guild'])
    for m in members:
        if m.is_bot: continue
        asyncio.create_task(activity_check(m.get_presence(), m))


async def activity_check(presence, user):
    if presence == None: return

    if len(presence.activities) != 0: 
        game = presence.activities[0].name
        if game == "Dota 2":
            asyncio.create_task(tools.grant_achievement(user, '20'))
        if game == "osu!":
            asyncio.create_task(tools.grant_achievement(user, '21'))
        if game == "League of Legends":
            asyncio.create_task(tools.grant_achievement(user, '22'))
        if game == "Minecraft" or\
           game == "Lunar Client" or\
           game == "LabyMod":
            asyncio.create_task(tools.grant_achievement(user, '23'))
        if game == 'Escape from Tarkov':
            asyncio.create_task(tools.grant_achievement(user, '26'))


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
