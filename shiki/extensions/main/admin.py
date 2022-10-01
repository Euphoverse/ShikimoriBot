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

import random
from xml.dom import HierarchyRequestErr
import lightbulb
import hikari
import logging
from shiki.utils import db, tools
import shiki


cfg = tools.load_data('./settings/config')
users = db.connect().get_database('shiki').get_collection('users')
plugin = lightbulb.Plugin("Admin")


@plugin.command
@lightbulb.add_checks(lightbulb.has_roles(cfg[cfg['mode']]['roles']['admin']))
@lightbulb.command(
    'admin',
    'Команды для администраторов',
    auto_defer=True
)
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def admin(ctx: lightbulb.SlashContext):
    # Command group /admin
    pass


@admin.child
@lightbulb.option(
    'user',
    'Получатель халявы',
    hikari.Member,
    required=False
)
@lightbulb.option(
    'amount',
    'Сумма халявы',
    int,
    required=True
)
@lightbulb.command(
    'increase',
    'Выдать пользователю деньги',
    auto_defer=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def add_money(ctx: lightbulb.SlashContext):
    if ctx.options.user is None:
        user = ctx.author
    else:
        user = ctx.options.user

    user_data = db.find_document(users, {'_id': user.id})
    user_data['money'] += ctx.options.amount
    db.update_document(users, {'_id': user.id}, {'money': user_data["money"]})
    await ctx.respond(embed=hikari.Embed(
        title='Успех',
        description=f'Выдано пользователю {user} {ctx.options.amount}! Новый баланс: {user_data["money"]}',
        color=shiki.Colors.SUCCESS
    ))


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
