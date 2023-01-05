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
from shiki.utils import tools


cfg = tools.load_data('./settings/config')


class VerificationTest(miru.Modal):
    text = miru.TextInput(label='Введите свой дискорд тег', 
                          style=hikari.TextInputStyle.SHORT,
                          placeholder='#0000',
                          required=True,
                          min_length=5,
                          max_length=5
    )

    async def callback(self, ctx: miru.ModalContext):
        if list(ctx.values.values())[0][1:] != str(ctx.user.discriminator):
            return await ctx.respond(
                embed=hikari.Embed(
                    title='Неверный тег',
                    description='Чтобы пройти верификацию вам нужно ввести свой #тег в открывшемся окне (#%s)' % (
                        ctx.user.discriminator
                    ),
                    color=shiki.Colors.ERROR
                ),
                flags=hikari.MessageFlag.EPHEMERAL
            )
        
        await ctx.member.add_role(
            cfg[cfg['mode']]['roles']['verify']
        )


class Verification(miru.View):
    def __init__(self, *args, **kwargs):
        super().__init__(timeout=None, *args, **kwargs)


    @miru.button(
        label='Верификация',
        style=hikari.ButtonStyle.SUCCESS,
        emoji='✅'
    )
    async def verify_button(self, button: miru.Button, ctx: miru.ViewContext):
        if cfg[cfg['mode']]['roles']['verify'] in ctx.member.role_ids:
            return await ctx.respond(embed=hikari.Embed(
                title='Действие отменено',
                description='Вы уже верифицировались! Начните общение в канале <#%s>' % cfg[cfg['mode']]['channels']['general'],
                color=shiki.Colors.ERROR
            ), flags=hikari.MessageFlag.EPHEMERAL)

        await ctx.member.add_role(
            cfg[cfg['mode']]['roles']['verify']
        )
        await ctx.respond(embed=hikari.Embed(
            title='Успешно',
            description='Вы верифицировались! Начните общение в канале <#%s>' % cfg[cfg['mode']]['channels']['general'],
            color=shiki.Colors.SUCCESS
        ), flags=hikari.MessageFlag.EPHEMERAL)
        await ctx.bot.rest.create_message(
            cfg[cfg['mode']]['channels']['general'],
            f"Хей, %s! Добро пожаловать на наш сервер! <3" % (
                ctx.user.mention
            )
        )
        # await ctx.respond_with_modal(VerificationTest('Ваш тег: #%s' % ctx.user.discriminator))
