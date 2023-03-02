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
import shiki
from shiki.utils import db, tools
import os


cfg = tools.load_data('./settings/config')
crystals = tools.load_data('./settings/crystals')
users = db.connect().get_database(os.environ['db']).get_collection('users')


def get_options() -> list:
    options = []
    for item in crystals['shop'].values():
        options.append(
            miru.SelectOption(
                label=item['display'],
                value=str(item['cost']),
                description="Цена: " + str(item['cost']) + " кристаллов"
            )
        )
    return options

class ShopView(miru.View):
    def __init__(self, plugin, *args, **kwargs):
        self.plugin = plugin
        super().__init__(timeout=10, *args, **kwargs)

    @miru.select(
        placeholder="Хотите что-то приобрести?",
        options=get_options()
    )
    async def buy_select(self, select: miru.Select, ctx: miru.ViewContext):
        data = db.find_document(users, {'_id': ctx.user.id})
        if data["crystals"] < int(select.values[0]):
            return await ctx.respond("haha no\nu poor", flags=hikari.MessageFlag.EPHEMERAL)
        
        item = None
        for i in crystals['shop'].values():
            if str(i['cost']) == select.values[0]:
                item = i
                break
        sure_msg = await ctx.respond(f"u sure you want to buy {item['display']}?\nY/N", flags=hikari.MessageFlag.EPHEMERAL)

        def check():
            return event.author_id == ctx.user.id and event.channel_id == ctx.channel_id
        
        while True:
            event = await self.plugin.bot.wait_for(
                hikari.GuildMessageCreateEvent,
                timeout=10
            )
            if check():
                break
        
        await sure_msg.delete()
        resp = event.message.content
        await event.message.delete()

        if resp.lower() not in ['y', 'ye', 'yes', 'д', 'да']:
            return await ctx.respond('транс отменён. погодите что', flags=hikari.MessageFlag.EPHEMERAL)
        
        await ctx.respond('ок бро без проблем', flags=hikari.MessageFlag.EPHEMERAL)
    
    async def on_timeout(self) -> None:
        for c in self.children:
            c.disabled = True
