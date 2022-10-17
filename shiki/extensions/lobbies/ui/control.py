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

import hikari
import miru
import shiki
from shiki.utils import db


users = db.connect().get_database('shiki').get_collection('users')


class InfoModal(miru.Modal):
    info = miru.TextInput(label='Информация о лобби')

    async def callback(self, ctx: miru.ModalContext):
        mg = await ctx.get_channel().fetch_history().last()
        embed = mg.embeds[0]
        embed.description = list(ctx.values.values())[0]
        await mg.edit(embed=embed)
        await ctx.bot.rest.create_message(ctx.channel_id, 'Информация о лобби обновлена', reply=mg)


class ControlView(miru.View):
    def __init__(self, owner_id: int, *args, **kwargs):
        self.owner_id = owner_id
        super().__init__(*args, **kwargs)

    @miru.button(label="Изменить инфо", style=hikari.ButtonStyle.SUCCESS)
    async def edit_info(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        modal = InfoModal('Изменение информации о лобби')
        await ctx.respond_with_modal(modal)

    @miru.button(label="Закрыть лобби", style=hikari.ButtonStyle.DANGER)
    async def basic_button(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        lobbies = db.find_document(users, {'_id': ctx.user.id})['lobbies']
        lobbies.remove(ctx.channel_id)
        db.update_document(users, {'_id': ctx.user.id}, {'lobbies': lobbies})
        await ctx.bot.rest.delete_channel(ctx.channel_id)
        self.stop()

    async def on_timeout(self) -> None:
        try:
            await self.message.fetch_channel()
        except hikari.NotFoundError:
            return
        await self.message.delete()

    async def view_check(self, ctx: miru.ViewContext) -> bool:
        if ctx.user.id != self.owner_id:
            await ctx.respond(embed=hikari.Embed(
                title='Вы не владелец лобби',
                description='Этим меню могут пользоваться только создатель лобби.',
                color=shiki.Colors.ERROR
            ), delete_after=5)
            return False
        return True
