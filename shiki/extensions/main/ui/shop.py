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
        super().__init__(timeout=120, *args, **kwargs)

    @miru.select(
        placeholder="Хотите что-то приобрести?",
        options=get_options()
    )
    async def buy_select(self, select: miru.Select, ctx: miru.ViewContext):
        item = None
        for i in crystals['shop'].values():
            if str(i['cost']) == select.values[0]:
                item = i
                break
        
        data = db.find_document(users, {'_id': ctx.user.id})
        if data["crystals"] < int(select.values[0]):
            return await ctx.respond(embed=hikari.Embed(
                title="Недостаточно средств",
                description=f"Вам не хватает {item['cost'] - data['crystals']}{crystals['emoji']} для покупки {item['display']} <:zerotwo_bored:1027903070572662834>",
                color=shiki.Colors.ERROR
            ), flags=hikari.MessageFlag.EPHEMERAL)
        
        sure_msg = await ctx.respond(embed=hikari.Embed(
                title="Подтверждение",
                description="Вы уверены, что хотите приобрести следующий товар?",
                color=shiki.Colors.WARNING
            )
            .add_field(f"{item['display']} {item['cost']}{crystals['emoji']}", "Да/Нет"), flags=hikari.MessageFlag.EPHEMERAL
        )

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

        if resp.lower() in ['y', 'ye', 'yes', 'д', 'да']:
            data["crystals"] -= item['cost']
            db.update_document(users, {'_id': ctx.user.id}, {"crystals": data["crystals"]})
            await ctx.respond(embed=hikari.Embed(
                title="Транзакция",
                description=f"Вы успешно приобрели ``{item['display']}`` за **{item['cost']}{crystals['emoji']}**\nК вам скоро обратиться администрация, ожидайте <:zerotwo_heart:1027903079410044958>",
                color=shiki.Colors.SPONSOR
            ), flags=hikari.MessageFlag.EPHEMERAL)

            await self.plugin.bot.rest.create_message(
                cfg[cfg['mode']]['channels']['mods_only'],
                f"<@{cfg[cfg['mode']]['users']['shop_manager']}>",
                embed=hikari.Embed(
                    title="Покупка в магазине кристаллов",
                    description=f"Пользователь `{ctx.user}` (`{ctx.user.id}`) приобрёл **``{item['display']}``**",
                    color=shiki.Colors.SPONSOR
                ),
                user_mentions=True
            )
            return
        
        await ctx.respond(embed=hikari.Embed(
            title="Транзакция",
            description=f"Покупка отменена.",
            color=shiki.Colors.WAIT
        ), flags=hikari.MessageFlag.EPHEMERAL)
