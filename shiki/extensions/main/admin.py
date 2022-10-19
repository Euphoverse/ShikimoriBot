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
from shiki.utils import db, tools, embeds
import shiki


cfg = tools.load_data('./settings/config')
achievements = tools.load_data('./settings/achievements')
tags = tools.load_data('./settings/tags')
users = db.connect().get_database('shiki').get_collection('users')
stats = db.connect().get_database('shiki').get_collection('stats')
plugin = lightbulb.Plugin("Admin")
currency_emoji = cfg['emojis']['currency']


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
@lightbulb.add_checks(lightbulb.has_roles(cfg[cfg['mode']]['roles']['admin']))
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
        description=f'Выдано пользователю **{user.username} {ctx.options.amount}{currency_emoji}**\nНовый баланс: **{user_data["money"]}{currency_emoji}**',
        color=shiki.Colors.SUCCESS
    ).set_footer(text='Выдача валюты', icon=ctx.author.display_avatar_url.url))



@admin.child
@lightbulb.add_checks(lightbulb.has_roles(cfg[cfg['mode']]['roles']['admin']))
@lightbulb.option(
    'user',
    'Жертва',
    hikari.Member,
    required=True
)
@lightbulb.command(
    'reset',
    'Обнулить статистику пользователя',
    auto_defer=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def reset_user(ctx: lightbulb.SlashContext):
    # Подтверждение
    user = ctx.options.user
    await ctx.respond(embed=hikari.Embed(
        title='Подтверждение',
        description=f'Вы уверены, что хотите обнулить статистику **{user}**?\n\n**Y/N**',
        color=shiki.Colors.WARNING
    ).set_footer(text='Обнуление статистики', icon=ctx.author.display_avatar_url.url))

    # Ожидание
    def check():
        return event.author_id == ctx.user.id and event.channel_id == ctx.channel_id
    
    while True:
        event = await plugin.bot.wait_for(
            hikari.GuildMessageCreateEvent,
            timeout=10
        )
        if check():
            break

    resp = event.message.content
    await event.message.delete()
    if(resp.lower() == 'y')|\
        (resp.lower() == 'ye')|\
        (resp.lower() == 'yes')|\
        (resp.lower() == 'yep'):

        # Обнуление
        db.update_document(users, {'_id': user.id}, cfg['db_defaults']['users'])
        db.update_document(stats, {'_id': user.id}, cfg['db_defaults']['stats'])
        await ctx.edit_last_response(embed=hikari.Embed(
            title='Выполнено',
            description=f'Статистика **{user}** была полностью обнулена.',
            color=shiki.Colors.SUCCESS
        ).set_footer(text='Обнуление статистики', icon=ctx.author.display_avatar_url.url))
    else:
        # Отмена
        await ctx.edit_last_response(embed=hikari.Embed(
            title='Отменено',
            description=f'Действие обнуления было отменено',
            color=shiki.Colors.ERROR
        ).set_footer(text='Обнуление статистики', icon=ctx.author.display_avatar_url.url))


@admin.child()
@lightbulb.add_checks(lightbulb.has_roles(cfg[cfg['mode']]['roles']['admin']))
@lightbulb.option(
    'user',
    'Пользователь',
    hikari.Member,
    required=False
)
@lightbulb.option(
    'achievement',
    'Номер ачивки',
    int,
    required=True
)
@lightbulb.command(
    'revoke',
    'Удалить ачивку у пользователя',
    auto_defer=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def remove_achievement(ctx: lightbulb.SlashContext):
    user = ctx.options.user
    if user == None: user = ctx.author
    a_id = str(ctx.options.achievement)
    asyncio.create_task(tools.revoke_achievement(user, a_id))
    await ctx.respond(embed=hikari.Embed(
        title='Выполнено',
        description=f'Ачивка ``#{a_id} - {achievements[a_id]["title"]}`` была удалена у **{user}**',
        color=shiki.Colors.SUCCESS
    ).set_footer(text='Обнуление ачивки', icon=ctx.author.display_avatar_url.url))


@admin.child()
@lightbulb.add_checks(lightbulb.has_roles(cfg[cfg['mode']]['roles']['admin']))
@lightbulb.option(
    'user',
    'Пользователь',
    hikari.Member,
    required=False
)
@lightbulb.option(
    'achievement',
    'Ачивка',
    str,
    required=True,
    choices=tools.get_force_achievements()
)
@lightbulb.command(
    'grant',
    'Выдать ачивку пользователю',
    auto_defer=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def give_achievement(ctx: lightbulb.SlashContext):
    user = ctx.options.user
    if user == None:
        user = ctx.author
    achievement = tools.get_achievement_id(ctx.options.achievement)
    given_succesfully = await tools.grant_achievement(user, achievement)
    if given_succesfully:
        await ctx.respond(embed=hikari.Embed(
            title='Выполнено',
            description=f'Ачивка ``#{achievement} - {ctx.options.achievement}`` была выдана **{user}**',
            color=shiki.Colors.SUCCESS
        ).set_footer(text='Выдача ачивки', icon=ctx.author.display_avatar_url.url))
    else:
        await ctx.respond(embed=hikari.Embed(
            title='Неудача',
            description=f'Ачивка ``#{achievement} - {ctx.options.achievement}`` уже имеется у **{user}**',
            color=shiki.Colors.ERROR
        ).set_footer(text='Выдача ачивки', icon=ctx.author.display_avatar_url.url))


@admin.child()
@lightbulb.add_checks(lightbulb.has_roles(cfg[cfg['mode']]['roles']['admin']))
@lightbulb.option(
    'user',
    'Пользователь',
    hikari.Member,
    required=False
)
@lightbulb.command(
    'view',
    'Узнать информацию о пользователе',
    auto_defer=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def get_info(ctx: lightbulb.SlashContext):
    user = ctx.options.user
    if user == None:
        user = ctx.author
    if user.is_bot:
        return await ctx.respond(embed=embeds.user_is_bot())
    data = db.find_document(users, {'_id': user.id})
    data2 = db.find_document(stats, {'_id': user.id})
    if data == None:
        return await ctx.respond(embed=embeds.user_not_found())
        
    em = hikari.Embed(
        title=f'Полная информация о {user.username}',
        color=shiki.Colors.SUCCESS
    ).set_footer(text='Информация', icon=ctx.author.display_avatar_url.url)
    
    _field1 = ''
    for d in data:
        _field1 += f"{d}: {data[d]}\n"
    em.add_field('Пользователь', f'```{_field1}```')

    _field2 = ''
    for d in data2:
        _field2 += f"{d}: {data2[d]}\n"
    em.add_field('Статистика', f'```{_field2}```')

    await ctx.respond(embed=em)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
