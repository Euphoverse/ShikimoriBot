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
import logging
from shiki.utils import db, tools
import shiki
from .ui import guides as guides_ui
from .ui import verification as verify


cfg = tools.load_data('./settings/config')
users = db.connect().get_database('shiki').get_collection('users')
plugin = lightbulb.Plugin("Guides")
_LOG = logging.getLogger('extensions.main.guides')


async def update_guides():
    guides = tools.load_data('./settings/guides', encoding='utf8')
    me = plugin.bot.get_me()

    for g in guides:
        comp = None
        if 'children' in guides[g]:
            comp = guides_ui.RootPage(g)
        
        if guides[g]['special-attribute'] == 'verification':
            comp = verify.Verification()

        history = await plugin.bot.rest.fetch_messages(guides[g]['channel'][cfg['mode']])
        if (history[0].author.id != me.id if len(history) != 0 else True):
            m = await plugin.bot.rest.create_message(
                channel=guides[g]['channel'][cfg['mode']],
                embed=tools.embed_from_dict(guides[g]['embed']),
                components=comp
            )
        else:
            m = await history[0].edit(
                embed=tools.embed_from_dict(guides[g]['embed']),
                components=comp
            )

        await comp.start(m)


@plugin.command
@lightbulb.command(
    'update_guides',
    'Перезагрузка всех файла guides.json'
)
@lightbulb.implements(lightbulb.SlashCommand)
async def update_guides_cmd(ctx: lightbulb.SlashContext):
    await ctx.respond(embed=hikari.Embed(
        title='Обновляю...',
        description='Запускаю процесс обновления всех гайдов',
        color=shiki.Colors.WAIT
    ))

    await update_guides()

    await ctx.edit_last_response(embed=hikari.Embed(
        title='Выполнено!',
        description='Все гайды успешно обновлены',
        color=shiki.Colors.SUCCESS
    ))


@plugin.listener(hikari.ShardReadyEvent)
async def auto_guides_update(event: hikari.ShardReadyEvent):
    _LOG.info('updating guides')
    await update_guides()
    _LOG.info('guides updated')


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
