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

import lightbulb
import hikari
from shiki.utils import db, tools, embeds
import shiki


cfg = tools.load_data('./settings/config')
achievements = tools.load_data('./settings/achievements')
users = db.connect().get_database('shiki').get_collection('users')
stats = db.connect().get_database('shiki').get_collection('stats')
plugin = lightbulb.Plugin("Achievements")


@plugin.command
@lightbulb.option(
    'user',
    'Пользователь',
    type=hikari.User,
    required=False
)
@lightbulb.option(
    'type',
    'Вид достижений',
    type=str,
    required=True,
    choices=['Полученные', 'Не полученные']
)
@lightbulb.command(
    'achievements',
    'Просмотреть ачивки'
)
@lightbulb.implements(lightbulb.SlashCommand)
async def view_achievemnts(ctx: lightbulb.SlashContext) -> None:
    user = ctx.options.user
    if user == None:
        user = ctx.author
    if user.is_bot:
        return await ctx.respond(embeds.user_is_bot())
    data = db.find_document(users, {'_id': user.id})
    if data == None:
        return await ctx.respond(embeds.user_not_found())
    
    aches = data['achievements']
    em = hikari.Embed(
        title=f'Достижения {user.username}',
        color=shiki.Colors.ACHIEVEMENT
    )

    output_fields = []
    output_field = ''
    for index, ac in achievements.items():
        pref = "⚫"
        title = ac['title']
        desc = f'- {ac["description"]}'
        add_field = ''
        if index in aches:
            pref = "🟢"
            if 'attributes' in ac and 'hidden' in ac['attributes']:
                pref = "🟡"
                desc = ''
            if ctx.options.type == "Полученные":
                add_field = f'{pref}{title} {desc}\n'
        else:
            if 'attributes' in ac and 'hidden' in ac['attributes']: continue
            if ctx.options.type == "Не полученные":
                add_field = f'{pref}{title} {desc}\n'
        if len(output_field) + len(add_field) > 1024:
            output_fields.append(output_field)
            output_field = ''
        output_field += add_field
        
    if output_field == '':
        output_field = "Достижений нет"
    output_fields.append(output_field)
    for index in range(len(output_fields)):
        title = 'Продолжение'
        if index == 0: title = 'Список достижений'
        em.add_field(title, f'```{output_fields[index]}```')
    await ctx.respond(embed=em)
        


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
