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
from shiki.utils import db, tools
from .ui import embed
import os


cfg = tools.load_data("./settings/config")
users = db.connect().get_database(os.environ["db"]).get_collection("users")
plugin = lightbulb.Plugin("MediaBroadcasts")


@plugin.command
@lightbulb.command("media", "Команды связанные с медиа", auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def media(ctx: lightbulb.SlashContext):
    # Command group /media
    pass


@media.child
@lightbulb.add_checks(lightbulb.has_roles(cfg[cfg["mode"]]["roles"]["p:create_embed"]))
@lightbulb.option(
    "channel",
    "Канал в котором будет опубликовано сообщение",
    hikari.TextableGuildChannel,
    required=True,
)
@lightbulb.command("new_embed", "Создать новое embed-сообщение")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def new_embed(ctx: lightbulb.SlashContext):
    view = embed.EmbedConstructor(ctx.options.channel.id, timeout=600)
    msg = await (
        await ctx.respond(embed=hikari.Embed(title="Нет заголовка"), components=view)
    ).message()
    await view.start(msg)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
