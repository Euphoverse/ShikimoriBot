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


cfg = tools.load_data('./settings/config')
users = db.connect().get_database('shiki').get_collection('users')
plugin = lightbulb.Plugin("Economy")


def add_xp(id, amount):
    db.update_document(users, {'_id': id},
                       {'xp':
                        db.find_document(users, {'_id': id})['xp'] + amount
                        })


@plugin.command
@lightbulb.command(
    'economy',
    'Команды связанные с системой экономики',
    auto_defer=True
)
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def economy(ctx: lightbulb.SlashContext):
    # /economy
    pass


@economy.child
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
@lightbulb.implements(lightbulb.SlashSubCommand)
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
    em.set_author(name=str(user), icon=user.display_avatar_url.url)

    em.add_field(
        'Спонсорка', 'нет' if data['sponsor'] is None else 'активна с ' + data['sponsor'])
    em.add_field('Всего пожертвовано', data['donated'], inline=True)
    em.add_field('Уровень', data['level'], inline=True)
    em.add_field('Опыт', '%s/%s' %
                 (data['xp'], tools.calc_xp(data['level'] + 1)), inline=True)
    em.add_field('Баланс', data['money'], inline=True)
    em.add_field('Приглашений', data['invites'], inline=True)

    await ctx.respond(embed=em)


@economy.child
@lightbulb.option(
    'user',
    'Пользователь',
    hikari.Member,
    required=True
)
@lightbulb.option(
    'amount',
    'Сумма',
    int,
    required=True
)
@lightbulb.command(
    'transfer',
    'Перевести деньги другому участнику',
    auto_defer=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def transfer(ctx: lightbulb.SlashContext):
    sender = ctx.author
    recipient = ctx.options.user

    if(sender.id == recipient.id):
        return await ctx.respond(embed=hikari.Embed(
            title='Ошибка',
            description='Вы не можете перевести деньги самому себе!',
            color=shiki.Colors.ERROR
        ))

    if(ctx.options.amount <= 0):
        return await ctx.respond(embed=hikari.Embed(
            title='Ошибка',
            description='Вы не можете перевести отрицательное количество средств!',
            color=shiki.Colors.ERROR
        ))

    sender_data = db.find_document(users, {'_id': sender.id})
    recipient_data = db.find_document(users, {'_id': recipient.id})

    if(sender_data['money'] < ctx.options.amount):
        return await ctx.respond(embed=hikari.Embed(
            title='Ошибка',
            description='Недостаточно средств!',
            color=shiki.Colors.ERROR
        ))

    updated_balance = sender_data['money'] - ctx.options.amount
    db.update_document(users, {'_id': sender.id}, {'money': updated_balance})
    updated_balance = recipient_data['money'] + ctx.options.amount
    db.update_document(users, {'_id': recipient.id},
                       {'money': updated_balance})

    await ctx.respond(embed=hikari.Embed(
        title='Выполнено!',
        description=f'Успешно переведено {ctx.options.amount} {recipient.username}!',
        color=shiki.Colors.SUCCESS
    ))


@economy.child
@lightbulb.option(
    'dice',
    'Номер кости (от 1 до 6)',
    int,
    required=True
)
@lightbulb.option(
    'bet',
    'Ставка',
    int,
    required=True
)
@lightbulb.command(
    'dice',
    'Кинуть кости',
    auto_defer=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def transfer(ctx: lightbulb.SlashContext):
    if(ctx.options.dice < 1) | (ctx.options.dice > 6):
        return await ctx.respond(embed=hikari.Embed(
            title='Ошибка',
            description='Выберите число кости от 1 до 6!',
            color=shiki.Colors.ERROR
        ))

    if(ctx.options.bet <= 0):
        return await ctx.respond(embed=hikari.Embed(
            title='Ошибка',
            description='Вы не можете поставить отрицательное количество средств!',
            color=shiki.Colors.ERROR
        ))

    r_dice = random.randint(1, 6)
    user = ctx.author
    user_data = db.find_document(users, {'_id': user.id})
    newbalance = user_data['money'] - ctx.options.bet

    if(r_dice == ctx.options.dice):
        # Ставка сыграла
        newbalance += ctx.options.bet * 6
        await ctx.respond(embed=hikari.Embed(
            title='Победа',
            description=f'Вы очень удачливы! Вы выиграли {ctx.options.bet * 6}.',
            color=shiki.Colors.SUCCESS
        ))
    else:
        # Ставка проиграна
        await ctx.respond(embed=hikari.Embed(
            title='Проигрыш',
            description=f'Увы, ваша ставка не сыграла. Вы проиграли {ctx.options.bet}.',
            color=shiki.Colors.ERROR
        ))
    db.update_document(users, {'_id': user.id}, {'money': newbalance})
    if(ctx.options.bet >= 1000):
        add_xp(user.id, 2)
    else:
        add_xp(user.id, 1)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
