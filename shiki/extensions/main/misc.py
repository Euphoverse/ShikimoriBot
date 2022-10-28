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
import random
import lightbulb
import hikari
from shiki.utils import db, tools
import shiki
import os


cfg = tools.load_data('./settings/config')
users = db.connect().get_database(os.environ['db']).get_collection('users')
plugin = lightbulb.Plugin("Misc")


@plugin.command
@lightbulb.command(
    'misc',
    'Разные вспомогательные команды',
    auto_defer=True
)
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def misc(ctx: lightbulb.SlashContext) -> None:
    # Command group /misc
    pass


@misc.child
@lightbulb.option(
    'sides',
    'Количество граней',
    type=int,
    required=True,
    min_value=2,
    max_value=101
)
@lightbulb.option(
    'cubes',
    'Количество кубиков',
    type=int,
    required=False,
    min_value=1,
    max_value=15,
    default=1
)
@lightbulb.command(
    'dice',
    'Кинуть кубики'
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def dice(ctx: lightbulb.SlashContext) -> None:
    asyncio.create_task(tools.grant_achievement(ctx.author, '24'))
    await ctx.respond(embed=hikari.Embed(
        title='Кубики',
        description='🎲 ' + ', '.join([str(random.randint(1, ctx.options.sides))
                              for _ in range(ctx.options.cubes)]),
        color=shiki.Colors.SUCCESS
    ))


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
