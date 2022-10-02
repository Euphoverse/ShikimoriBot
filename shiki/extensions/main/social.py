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

from re import S
from sre_constants import SUCCESS
import lightbulb
import hikari
from shiki.utils import db, tools
import shiki


cfg = tools.load_data('./settings/config')
users = db.connect().get_database('shiki').get_collection('users')
plugin = lightbulb.Plugin("Social")
currency_emoji = cfg['emojis']['currency']
emoji_denied = cfg['emojis']['access_denied']


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
    elif ctx.options.user.is_bot:
        user = ctx.author
        return await ctx.respond(embed=hikari.Embed(
            title='Ошибка',
            description='У ботов нет профилей!',
            color=shiki.Colors.ERROR
        ).set_footer(text=f'{emoji_denied} Некорректные данные'))
    else:
        user = ctx.options.user

    data = db.find_document(users, {'_id': user.id})
    em = hikari.Embed(
        title=f'Профиль пользователя {user.username}',
        color=shiki.Colors.SUCCESS if data['sponsor'] is None else shiki.Colors.SPONSOR
    )
    em.set_footer(text=f'Запросил {ctx.author.username}',
                  icon=ctx.author.display_avatar_url.url)
    em.set_thumbnail(user.display_avatar_url.url)

    em.add_field(
        'Спонсорка', '```Отсутствует```' if data['sponsor'] is None else '```Активна с ' + data['sponsor'] + '```')
    em.add_field('Всего пожертвовано', f"```{data['donated']} рублей```", inline=True)
    em.add_field('Уровень', f"```{data['level']}```", inline=True)
    em.add_field('Опыт', '```%s/%s```' %
                 (round(data['xp']), round(tools.calc_xp(data['level'] + 1))), inline=True)
    em.add_field('Баланс', f'```{data["money"]}{currency_emoji}```', inline=True)
    em.add_field('Приглашений', f"```{data['invites']}```", inline=True)

    await ctx.respond(embed=em)


@plugin.command
@lightbulb.option(
    'type',
    'Тип списка',
    str,
    required=True,
    choices=['xp', 'money', 'donated', 'invites']
)
@lightbulb.command(
    'leaderboard',
    'Список лидеров',
    auto_defer=True
)
@lightbulb.implements(lightbulb.SlashCommand)
async def leaderboard(ctx: lightbulb.SlashContext):
    """ Data sort """
    all_data = db.find_document(users, {}, multiple=True)
    data = {}
    type = ctx.options.type
    for sdata in all_data:
        if sdata[type] != 0: 
            data[sdata['_id']] = sdata[type]
    data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))

    """ Embed construction """
    em = hikari.Embed(
        title=f'Список лидеров по `{ctx.options.type}`',
        color=shiki.Colors.SUCCESS
    ).set_footer(text=f'Запросил {ctx.author.username}',
                 icon=ctx.author.display_avatar_url.url)
    index = 1
    guild = ctx.get_guild()
    suff = ''
    if type == 'money': suff = currency_emoji
    for sdata in data:
        pref = ''
        if type == 'xp': suff = f' | **Level**: {tools.calc_lvl(data[sdata])}'
        if index == 3: pref = "🥉 "
        if index == 2: pref = "🥈 "
        if index == 1: pref = "🥇 "
        em.add_field(f'**{pref}#{index}. {guild.get_member(sdata).username}**', f'**{type.capitalize()}**: {data[sdata]}{suff}')
        index += 1
    await ctx.respond(em)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
