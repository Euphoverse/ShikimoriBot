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

import miru
import hikari
from lightbulb.ext import tasks
import aiohttp
import shiki
import os


class Leaderboard(miru.View):
    def __init__(self, *args, **kwargs):
        Leaderboard.last_instance = self
        super().__init__(timeout=None, *args, **kwargs)


    @miru.button(
        label='Обновить',
        style=hikari.ButtonStyle.SECONDARY,
        emoji='🔄'
    )
    async def update_button(self, button: miru.Button, ctx: miru.ViewContext):
        await ctx.respond(embed=hikari.Embed(
            title='Обновляю',
            description='Локальный топ будет скоро обновлён.',
            color=shiki.Colors.WAIT
        ), flags=hikari.MessageFlag.EPHEMERAL)
        await update_leaderboard()
    

@tasks.task(m=5)
async def auto_update():
    await update_leaderboard()

async def update_leaderboard():
    board = Leaderboard.last_instance
    async with aiohttp.ClientSession('https://api.euphoverse.moe') as s:
        async with s.get(
            '/admin/osu/leaderboard',
            params={'guild': (await board.message.fetch_channel()).guild_id},
            headers={'key': os.environ['api_key']}
        ) as resp:
            r = resp
            json = await r.json()

    if r.status != 200:
        board.message.embeds[-1].description = 'Siesta API {} Error (https://api.euphoverse.moe): {}'.format(
            r.status, (json)
        )
    else:
        res = []
        for place, data in enumerate(json['data']):
            res.append("**{}.** <@{}> ({}: {}pp {}% #{:,})".format(
                place + 1, data['discord_id'],
                data['osu_name'], round(data['pp']),
                round(data['acc']), round(data['rank'])
            ))
        board.message.embeds[-1].description = '\n'.join(res)
    
    await board.message.edit(
        embeds=board.message.embeds
    )