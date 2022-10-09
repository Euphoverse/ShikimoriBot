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
from hikari import Embed, User
from shiki.utils import db, tools
import shiki


users = db.connect().get_database('shiki').get_collection('users')
cfg = tools.load_data('./settings/config')
emoji_denied = cfg['emojis']['access_denied']
currency_emoji = cfg['emojis']['currency']


def profile(user: User, author: User):
    if user.is_bot:
        return user_is_bot()
    data = db.find_document(users, {'_id': user.id})
    if data == None:
        return user_not_found()
    if data['money'] == 555 and user.id == author.id: 
        asyncio.create_task(tools.grant_achievement(user, '18'))
    if data['money'] > 10000 and user.id == author.id:
        asyncio.create_task(tools.grant_achievement(user, '19'))
    em = Embed(
        title=f'Профиль пользователя {user.username}',
        color=shiki.Colors.SUCCESS if data['sponsor'] is None else shiki.Colors.SPONSOR
    )
    em.set_footer(text=f'Запросил {author.username}',
                icon=author.display_avatar_url.url)
    em.set_thumbnail(user.display_avatar_url.url)

    em.add_field(
        'Спонсорка', '```Отсутствует```' if data['sponsor'] is None else '```Активна с ' + data['sponsor'] + '```')
    em.add_field('Всего пожертвовано', f"```{data['donated']} рублей```", inline=True)
    em.add_field('Уровень', f"```{data['level']}```", inline=True)
    em.add_field('Опыт', '```%s/%s```' %
                (round(data['xp']), round(tools.calc_xp(data['level'] + 1))), inline=True)
    em.add_field('Баланс', f'```{data["money"]}{currency_emoji}```', inline=True)
    em.add_field('Приглашений', f"```{data['invites']}```", inline=True)

    return em

def user_not_found():
    return Embed(
        title='Ошибка',
        description='Пользователя нет в базе данных!',
        color=shiki.Colors.ERROR
    ).set_footer(text=f'{emoji_denied} Пользователь не найден')

def user_is_bot():
    return Embed(
        title='Ошибка',
        description='К ботам не применимы команды!',
        color=shiki.Colors.ERROR
    ).set_footer(text=f'{emoji_denied} Некорректные данные')
