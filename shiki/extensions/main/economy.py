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

from datetime import datetime, timedelta
import random
import lightbulb
import hikari
from shiki.utils import db, tools
import shiki


cfg = tools.load_data('./settings/config')
users = db.connect().get_database('shiki').get_collection('users')
plugin = lightbulb.Plugin("Economy")
currency_emoji = cfg['emojis']['currency']


def add_xp(id, amount):
    data = db.find_document(users, {'_id': id})
    xp = data['xp']

    xp += amount
    needed_xp = tools.calc_xp(data['level'] + 1)

    levelup = False

    if(xp >= needed_xp):
        xp -= needed_xp
        data['level'] += 1
        levelup = True

    db.update_document(users, {'_id': id}, {'level': data['level'], 'xp': xp})
    return levelup


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
        title=f'Профиль пользователя {user.username}',
        color=shiki.Colors.SUCCESS if data['sponsor'] is None else shiki.Colors.SPONSOR
    )
    em.set_footer(text=f'Запросил {ctx.author.username}', icon=ctx.author.display_avatar_url.url)
    em.set_thumbnail(user.display_avatar_url.url)

    em.add_field(
        'Спонсорка', 'нет' if data['sponsor'] is None else 'активна с ' + data['sponsor'])
    em.add_field('Всего пожертвовано', data['donated'], inline=True)
    em.add_field('Уровень', data['level'], inline=True)
    em.add_field('Опыт', '%s/%s' %
                 (data['xp'], round(tools.calc_xp(data['level'] + 1))), inline=True)
    em.add_field('Баланс', f'{data["money"]}{currency_emoji}', inline=True)
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
    required=True,
    min_value=1
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
        ).set_footer(text=str(sender), icon=sender.display_avatar_url.url))

    sender_data = db.find_document(users, {'_id': sender.id})
    recipient_data = db.find_document(users, {'_id': recipient.id})

    if(sender_data['money'] < ctx.options.amount):
        return await ctx.respond(embed=hikari.Embed(
            title='Ошибка',
            description='Недостаточно средств!',
            color=shiki.Colors.ERROR
        ).set_footer(text=str(sender), icon=sender.display_avatar_url.url))

    updated_balance = sender_data['money'] - ctx.options.amount
    db.update_document(users, {'_id': sender.id}, {'money': updated_balance})
    updated_balance = recipient_data['money'] + ctx.options.amount
    db.update_document(users, {'_id': recipient.id},
                       {'money': updated_balance})

    await ctx.respond(embed=hikari.Embed(
        title='Выполнено!',
        description=f'Успешно переведено {ctx.options.amount}{currency_emoji} {recipient.username}!',
        color=shiki.Colors.SUCCESS
    ).set_footer(text=f'Отправитель: {sender.username}', icon=sender.display_avatar_url.url))


@economy.child
@lightbulb.add_cooldown(90, 5, lightbulb.UserBucket)
@lightbulb.option(
    'dice',
    'Номер кости (от 1 до 6)',
    int,
    required=True,
    min_value=1,
    max_value=6
)
@lightbulb.option(
    'bet',
    'Ставка',
    int,
    required=True,
    min_value=1
)
@lightbulb.command(
    'dice',
    'Кинуть кости',
    auto_defer=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def dice(ctx: lightbulb.SlashContext):
    r_dice = random.randint(1, 6)
    user = ctx.author
    user_data = db.find_document(users, {'_id': user.id})
    newbalance = user_data['money'] - ctx.options.bet

    if(r_dice == ctx.options.dice):
        # Ставка сыграла
        newbalance += ctx.options.bet * 6
        await ctx.respond(embed=hikari.Embed(
            title='Победа',
            color=shiki.Colors.SUCCESS
        ).set_footer(text=f'{user.username} сыграл в кости', icon=user.display_avatar_url.url)
        .add_field(f'Вы очень удачливы! Вы выиграли **{ctx.options.bet * 6}**.',
        f'Выпало **{r_dice}**\nВы поставили на **{ctx.options.dice}**', inline=False))
    else:
        # Ставка проиграна
        await ctx.respond(embed=hikari.Embed(
            title='Проигрыш',
            color=shiki.Colors.ERROR
        ).set_footer(text=f'{user.username} сыграл в кости', icon=user.display_avatar_url.url)
        .add_field(f'Увы, ваша ставка не сыграла. Вы проиграли **{ctx.options.bet}**.',
        f'Выпало **{r_dice}**\nВы поставили на **{ctx.options.dice}**', inline=False))

    if(ctx.options.bet >= 1000):
        levelup = add_xp(user.id, 3)
    else:
        levelup = add_xp(user.id, 1)
    if(levelup == True):
        newlevel = db.find_document(users, {'_id': user.id})['level']
        reward = newlevel * 25 + 100
        newbalance += reward
        name = user.username
        await ctx.get_guild()\
                 .get_channel(cfg[cfg['mode']]['channels']['actions'])\
                 .send(user.mention, embed=hikari.Embed(
                     title='Повышение уровня',
                     description=f'{name} достиг **{newlevel}** уровня! Награда: **{reward}**{currency_emoji}',
                     color=shiki.Colors.SUCCESS
                 ).set_footer(text='Повышение уровня', icon=user.display_avatar_url.url))

    db.update_document(users, {'_id': user.id}, {'money': newbalance})


@economy.child
@lightbulb.command(
    'daily',
    'Получить ежедневный бонус',
    auto_defer=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def daily(ctx: lightbulb.SlashContext):
    user = ctx.author
    data = db.find_document(users, {'_id': user.id})
    bonus = random.randint(203, 210)
    add_xp(user.id, 5)
    if(data['last_daily'] == 0) or (datetime.now() - data['last_daily'] > timedelta(days=1)):
        db.update_document(users, {'_id': user.id},
                           {'money': data['money'] + bonus,
                           'last_daily': datetime.now()})
        await ctx.respond(embed=hikari.Embed(
            title='Бонус',
            description=f'Вы получили свой ежедневный бонус: {bonus}{currency_emoji}.',
            color=shiki.Colors.SUCCESS
        ).set_footer(text=str(user.username), icon=user.display_avatar_url.url))
    else:
        time_left = timedelta(days=1) - (datetime.now() - data['last_daily'])
        await ctx.respond(embed=hikari.Embed(
            title='Не так быстро!',
            description=f'Ежедневный бонус будет доступен через: {str(time_left).split(".")[0]}.',
            color=shiki.Colors.SUCCESS
        ).set_footer(text=str(user.username), icon=user.display_avatar_url.url))


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
