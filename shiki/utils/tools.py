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

import json
import re
from typing import Any, List
from hikari import Embed, File, Guild, Member, Color
import os
from random import choice

import hikari
import lightbulb
from shiki.utils import db
import shiki
SETTINGS_PATH = './settings/%s.json'
DATA_PATH = './data/%s.json'


users = db.connect().get_database('shiki').get_collection('users')


def embed_from_dict(data: dict) -> Embed:
    embed = Embed(
        title=data.get('title', None),
        description=data.get('description', None),
        url=data.get('url', None),
        color=Color.from_hex_code(data.get('color', None)),
        timestamp=data.get('timestamp', None)
    )
    if 'footer' in data:
        embed.set_footer(
            data['footer'].get('text', None),
            icon=data['footer'].get('icon_url', None)
        )

    if 'image' in data:
        embed.set_image(
            data['image'].get('url', None)
        )

    if 'thumbnail' in data:
        embed.set_thumbnail(
            data['thumbnail'].get('url')
        )

    if 'author' in data:
        embed.set_author(
            name=data['author'].get('name', None),
            url=data['author'].get('url', None),
            icon=data['author'].get('icon_url', None)
        )

    if 'fields' in data:
        for field in data['fields']:
            embed.add_field(
                field['name'],
                field['value'],
                inline=field.get('inline', False)
            )

    return embed


def calc_xp(lvl):
    '''Calculates amount of xp needed to levelup'''
    lvl -= 1
    return ((2 * lvl ** 2 + 27 * lvl + 91) * lvl * 5) / 6


def calc_lvl(xp):
    '''Calculates level from amount of xp'''
    level = 0
    while xp > calc_xp(level + 1):
        level += 1
    return level


def embed_img(embed: Embed, img: str) -> dict:
    '''Adds local image to embed and returns kwargs needed to send embed'''
    embed.set_thumbnail(url='attachment://' + img.split('/')[-1])
    return {'embed': embed, 'files': [File(img)]}


def emotion(embed: Embed, category: str) -> dict:
    '''Adds random thumbnail from category to embed'''
    return embed_img(embed, f'./images/{category}/{choice(os.listdir("./images/" + category))}')


def calc_coins(lvl: int) -> int:
    '''Calculates reward for leveling up'''
    return 80


def get_mod_users(mod_id: int) -> List[int]:
    '''Returns list of users, who were assigned to mod with passed mod_id'''
    return [doc['_id'] for doc in db.find_document(users, {}, True) if doc['mod'] == mod_id]


def load_data(name: str, encoding='utf8') -> dict | list | None:
    '''Loads json file'''
    if os.path.isfile(name + '.json'):
        with open(name + '.json', 'r', encoding=encoding) as f:
            return json.load(f)


def update_data(name: str, data: dict | list, encoding='utf8') -> None:
    '''Updates json file'''
    if os.path.isfile(name + '.json'):
        with open(name + '.json', 'w', encoding=encoding) as f:
            return json.dump(data, f)


def get(iter, **kwargs) -> Any:
    for item in iter:
        if all([eval('item.%s' % key) == kwargs[key] for key in kwargs.keys()]):
            return item


cfg = load_data('./settings/config')


def get_mods(guild: Guild) -> List[Member]:
    '''Returns list of all mods on the server (users with specific roles)'''
    mod_roles = [cfg[cfg['mode']]['roles'][id] for id in cfg['mod_roles']]
    mods = []
    for m in guild.get_members():
        member = guild.get_member(m)
        if set(member.role_ids).intersection(mod_roles) != set():
            mods.append(member)
    return mods


async def add_xp(user: hikari.Member, amount: int, ctx: lightbulb.SlashContext):
    data = db.find_document(users, {'_id': user.id})
    xp = data['xp'] + amount
    needed_xp = calc_xp(data['level'] + 1)
    reward = 0

    while xp >= needed_xp:
        data['level'] += 1
        needed_xp = calc_xp(data['level'] + 1)
        reward += calc_coins(data['level'])
        await ctx.bot.rest.create_message(
            channel=cfg[cfg['mode']]['channels']['actions'],
            embed=Embed(
                title='Повышение уровня',
                description=f'{user.username} достиг **{data["level"]}** уровня! Награда: **{reward}**{cfg["emojis"]["currency"]}',
                color=shiki.Colors.SUCCESS
            ).set_footer(text='Повышение уровня', icon=user.display_avatar_url.url)
        )

    db.update_document(users,
                       {'_id': user.id},
                       {'level': data['level'], 'xp': xp,
                        'money': data['money'] + reward}
                       )

def fetch_content(content):
    output = None
    if re.search('закреп', content): output = 'pin'
    if re.search(' ава', content): output = 'avatar'
    if re.search(' аву', content): output = 'avatar'
    if re.search('фотокарточк', content): output = 'avatar'
    if re.search(' заш', content): output = 'join'
    if re.search('присоединил', content): output = 'join'
    if re.search(' мск', content): output = 'msk'
    if re.search(' врем', content): output = 'msk'
    if re.search('прошло', content): output = 'time since'
    if re.search(' мод', content): output = 'mod'
    if re.search('слоумод', content): output = 'slowmode'
    if re.search('медленный', content): output = 'slowmode'
    if re.search(' онлайн', content): output = 'online'
    if re.search('сноуфлейк', content): output = 'snowflake'
    if re.search('перемести', content): output = 'move'
    if re.search('перетащи', content): output = 'move'
    if re.search('перекинь', content): output = 'move'
    if re.search('мут всем', content): output = 'mute all'
    if re.search('анмут всем', content): output = 'mute all'
    if re.search('гк мут', content): output = 'mute all'
    if re.search('гк анмут', content): output = 'mute all'
    if re.search('замуть всех', content): output = 'mute all'
    if re.search('размуть всех', content): output = 'mute all'
    if re.search('замуть гк', content): output = 'mute all'
    if re.search('размуть гк', content): output = 'mute all'
    return output


achievements = load_data('./settings/achievements')


async def grant_achievement(user: hikari.User, achievement):
    data = db.find_document(users, {'_id': user.id})
    if data['achievements'] == None: return False
    if achievement in data['achievements']: return False
    else: 
        achs = data['achievements']
        achs.append(achievement)
        db.update_document(users, {'_id': user.id}, {'achievements': achs})
        achievement_title = achievements[achievement]['title']
        achievement_desc = achievements[achievement]['description']
        await user.app.rest.create_message(
            cfg[cfg['mode']]['channels']['actions'],
            f'{user.mention}, вы получили достижение:\n``{achievement_title} - {achievement_desc}``',
            user_mentions=True)
        return True


async def revoke_achievement(user: hikari.User, achievement):
    data = db.find_document(users, {'_id': user.id})
    if data['achievements'] == None: return False
    if achievement not in data['achievements']: return False
    else: 
        achievements = data['achievements']
        achievements.remove(achievement)
        db.update_document(users, {'_id': user.id}, {'achievements': achievements})
        return True