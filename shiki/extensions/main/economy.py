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
import lightbulb
import hikari
import logging
from shiki.utils import db, tools
import shiki


cfg = tools.load_file('config')
users = db.connect().get_database('shiki').get_collection('users')
plugin = lightbulb.Plugin("Economy")


@plugin.command
@lightbulb.option(
    'user',
    'Пользователь',
    hikari.Member,
    required=False
)
@lightbulb.command(
    'profile',
    'Просмотреть профиль пользователя',
    auto_defer=True
)
@lightbulb.implements(lightbulb.SlashCommand)
async def profile(ctx: lightbulb.SlashContext):
    if ctx.options.user is None:
        user = ctx.author
    else:
        user = ctx.options.user

    data = db.find_document(users, {'_id': user.id})
    em = hikari.Embed(
        title='Профиль пользователя',
        color=shiki.Colors.SUCCESS if data['sponsor'] is None else shiki.Colors.SPONSOR
    )
    em.set_author(name=str(user), url=user.display_avatar_url.url)

    em.add_field(
        'Спонсорка', 'нет' if data['sponsor'] is None else 'активна с ' + data['sponsor'])
    em.add_field('Всего пожертвовано', data['donated'], inline=True)
    em.add_field('Уровень', data['level'], inline=True)
    em.add_field('Опыт', '%s/%s' %
                 (data['xp'], tools.calc_xp(data['level'] + 1)), inline=True)
    em.add_field('Баланс', data['money'], inline=True)
    em.add_field('Приглашений', data['invites'], inline=True)

    await ctx.respond(embed=em)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
