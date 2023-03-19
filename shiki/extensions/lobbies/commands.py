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
import shiki
from .ui import control
import os


cfg = tools.load_data("./settings/config")
users = db.connect().get_database(os.environ["db"]).get_collection("users")
plugin = lightbulb.Plugin("LobbiesCommands")


@plugin.command
@lightbulb.command("lobby", "Команды связанные с системой лобби", auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def lobby(ctx: lightbulb.SlashContext):
    # Command group /lobby
    pass


@lobby.child
@lightbulb.option(
    "info", "Информация о комнате", str, required=False, default="Нет информации"
)
@lightbulb.option(
    "auto_move",
    "Включение автоматического переноса в ГК",
    str,
    required=False,
    choices=["вкл.", "выкл."],
    default=False,
)
@lightbulb.command("create", "Создать новое лобби")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def create(ctx: lightbulb.SlashContext):
    data = db.find_document(users, {"_id": ctx.user.id})
    if len(data["lobbies"]) < 2:
        channel = await plugin.bot.rest.create_guild_voice_channel(
            ctx.guild_id,
            str(ctx.user),
            category=cfg[cfg["mode"]]["categories"]["lobbies"],
            permission_overwrites=[
                hikari.PermissionOverwrite(
                    id=ctx.user.id,
                    type=hikari.PermissionOverwriteType.MEMBER,
                    allow=(
                        hikari.Permissions.VIEW_CHANNEL
                        | hikari.Permissions.DEAFEN_MEMBERS
                        | hikari.Permissions.MUTE_MEMBERS
                    ),
                ),
                hikari.PermissionOverwrite(
                    id=ctx.guild_id,
                    type=hikari.PermissionOverwriteType.ROLE,
                    deny=(hikari.Permissions.VIEW_CHANNEL),
                ),
            ],
        )

        embed = hikari.Embed(
            title="Лобби пользователя %s" % str(ctx.user),
            description=ctx.options.info or "нет описания",
            color=shiki.Colors.SUCCESS,
        )
        embed.set_thumbnail(ctx.user.display_avatar_url.url)
        embed.set_footer("/lobby control для управления лобби")
        await channel.send(embed=embed)
        if ctx.options.auto_move == "вкл.":
            voice = ctx.get_guild().get_voice_state(ctx.user)
            if voice is None:
                await ctx.respond(
                    embed=hikari.Embed(
                        title="Канал создан",
                        description="Вас неудалось переместить в канал <#%s>"
                        % channel.id,
                        color=shiki.Colors.SUCCESS,
                    )
                )
                return
            await ctx.member.edit(voice_channel=channel)
            await ctx.respond(
                embed=hikari.Embed(
                    title="Канал создан",
                    description="Вы перемещены в канал <#%s>" % channel.id,
                    color=shiki.Colors.SUCCESS,
                )
            )
        else:
            await ctx.respond(
                embed=hikari.Embed(
                    title="Канал создан",
                    description="Вы можете зайти в канал <#%s> и использовать команду /lobby control для изменения параметров"
                    % channel.id,
                    color=shiki.Colors.SUCCESS,
                )
            )
        data["lobbies"].append(channel.id)
        db.update_document(users, {"_id": ctx.user.id}, {"lobbies": data["lobbies"]})
        return

    await ctx.respond(
        embed=hikari.Embed(
            title="Слишком много лобби",
            description="Попробуйте удалить некоторые свои лобби чтобы создать новые (лимит - 2)",
            color=shiki.Colors.ERROR,
        )
    )


async def owner_check(ctx: lightbulb.SlashContext):
    if ctx.channel_id not in db.find_document(users, {"_id": ctx.user.id})["lobbies"]:
        await ctx.respond(
            embed=hikari.Embed(
                title="Вы не владелец лобби",
                description="Эту команду может использовать только владелец лобби",
                color=shiki.Colors.ERROR,
            )
        )
        return False
    return True


@lobby.child
@lightbulb.command("control", "Управление лобби", ephemeral=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def create(ctx: lightbulb.SlashContext):
    if not await owner_check(ctx):
        return
    view = control.ControlView(ctx.user.id, timeout=300)
    msg = await ctx.respond(
        embed=hikari.Embed(
            title="Панель управления",
            description="К этой панели имеете доступ только вы. Используйте команду /lobby add чтобы добавить новых пользователей в лобби",
            color=shiki.Colors.SUCCESS,
        ),
        components=view,
    )
    await view.start(await msg.message())


@lobby.child
@lightbulb.option(
    "user",
    "Пользователь которого вы хотите добавить в лобби",
    hikari.Member,
    required=True,
)
@lightbulb.command("add", "Добавить пользователя в лобби")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def add(ctx: lightbulb.SlashContext):
    if not await owner_check(ctx):
        return

    if ctx.user.id == ctx.options.user.id:
        await ctx.respond(
            embed=hikari.Embed(
                title="Действие отменено",
                description="Вы не можете добавить самого себя в лобби",
                color=shiki.Colors.ERROR,
            )
        )
        return

    await plugin.bot.rest.edit_permission_overwrite(
        ctx.channel_id, ctx.options.user, allow=hikari.Permissions.VIEW_CHANNEL
    )
    await ctx.respond(
        embed=hikari.Embed(
            title="Пользователь добавлен",
            description="Теперь пользователь сможет присоединиться к вам в голосовой канал",
            color=shiki.Colors.SUCCESS,
        )
    )

    perms = ctx.get_channel().permission_overwrites
    added_users = (
        len([0 for u in perms if perms[u].allow.all(hikari.Permissions.VIEW_CHANNEL)])
        - 1
    )
    if added_users == 1:
        await tools.grant_achievement(ctx.user, "47")
    if added_users == 10:
        await tools.grant_achievement(ctx.user, "48")


@lobby.child
@lightbulb.option(
    "user",
    "Пользователь которого вы хотите убрать из лобби",
    hikari.Member,
    required=True,
)
@lightbulb.command("remove", "Убрать пользователя из лобби")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def remove(ctx: lightbulb.SlashContext):
    if not await owner_check(ctx):
        return

    if ctx.user.id == ctx.options.user.id:
        await ctx.respond(
            embed=hikari.Embed(
                title="Действие отменено",
                description="Вы не можете убрать самого себя из лобби",
                color=shiki.Colors.ERROR,
            )
        )
        return

    await plugin.bot.rest.edit_permission_overwrite(
        ctx.channel_id, ctx.options.user, deny=hikari.Permissions.VIEW_CHANNEL
    )
    await ctx.respond(
        embed=hikari.Embed(
            title="Пользователь убран",
            description="Пользователь будет выгнан из голосового канала",
            color=shiki.Colors.SUCCESS,
        )
    )
    voice = ctx.get_guild().get_voice_state(ctx.options.user)
    if voice is not None and voice.channel_id == ctx.channel_id:
        await ctx.options.user.edit(voice_channel=None)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
