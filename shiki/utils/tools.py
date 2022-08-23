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
from typing import List
from hikari import Embed, File, Guild, Member
import os
from random import choice
from shiki.utils import db


users = db.connect().get_database('shiki').get_collection('users')


def calc_xp(lvl):
    '''Calculates amount of xp needed to levelup'''
    return ((2 * lvl ** 2 + 27 * lvl + 91) * lvl * 5) / 6


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


def get_mods(guild: Guild) -> List[Member]:
    '''Returns list of all mods on the server (users with specific roles)'''
    raise NotImplemented


def load_file(name: str) -> dict | list | None:
    '''Loads json file with passed name from ./settings folder'''
    if os.path.isfile('./settings/%s.json' % name):
        with open('./settings/%s.json' % name, 'r') as f:
            return json.load(f)


def update_file(name: str, data: dict | list) -> None:
    '''Updates json file with passed name from ./settings folder'''
    if os.path.isfile('./settings/%s.json' % name):
        with open('./settings/%s.json' % name, 'r') as f:
            return json.dump(data, f)
