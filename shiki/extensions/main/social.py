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
import os


cfg = tools.load_data("./settings/config")
users = db.connect().get_database(os.environ["db"]).get_collection("users")
stats = db.connect().get_database(os.environ["db"]).get_collection("stats")
plugin = lightbulb.Plugin("Social")
currency_emoji = cfg["emojis"]["currency"]
emoji_denied = cfg["emojis"]["access_denied"]


@plugin.command
@lightbulb.option("user", "Пользователь", hikari.Member, required=False)
@lightbulb.command("profile", "Просмотреть профиль пользователя", auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def profile(ctx: lightbulb.SlashContext):
    if ctx.options.user is None:
        user = ctx.author
    else:
        user = ctx.options.user
    await ctx.respond(embed=embeds.profile(user, ctx.author))


@plugin.command
@lightbulb.command("Профиль пользователя", "Просомтреть профиль пользователя")
@lightbulb.implements(lightbulb.UserCommand)
async def profile_user(ctx: lightbulb.UserContext):
    ctx.user
    await ctx.respond(
        embed=embeds.profile(ctx.options.target, ctx.author),
        flags=hikari.MessageFlag.EPHEMERAL,
    )


@plugin.command
@lightbulb.option(
    "type",
    "Тип списка",
    str,
    required=True,
    choices=["xp", "money", "donated", "invites", "time_in_vc"],
)
@lightbulb.command("leaderboard", "Список лидеров", auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def leaderboard(ctx: lightbulb.SlashContext):
    """Data sort"""
    if ctx.options.type == "time_in_vc":
        all_data = db.find_document(stats, {}, multiple=True)
    else:
        all_data = db.find_document(users, {}, multiple=True)
    data = {}
    type = ctx.options.type
    for sdata in all_data:
        if sdata[type] != 0:
            data[sdata["_id"]] = sdata[type]
    data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))

    """ Embed construction """
    em = hikari.Embed(
        title=f"Список лидеров по `{type}`", color=shiki.Colors.SUCCESS
    ).set_footer(
        text=f"Запросил {ctx.author.username}", icon=ctx.author.display_avatar_url.url
    )
    index = 1
    guild = ctx.get_guild()
    suff = ""
    if type == "money":
        suff = currency_emoji
    for user_id in list(data)[:10]:
        user = guild.get_member(user_id)
        if user == None:
            username = f"(пользователь вышел)"
        else:
            username = user.username
        pref = ""
        if type == "xp":
            suff = f" | **Level**: {tools.calc_lvl(data[user_id])}"
        if type == "time_in_vc":
            vc_time = data[user_id]
            hh = round(vc_time // 3600)
            mm = round((vc_time // 60) % 60)
            ss = round(vc_time % 60)
            if mm < 10:
                mm = f"0{mm}"
            if ss < 10:
                ss = f"0{ss}"
            data[user_id] = f"{hh}:{mm}:{ss}"
        pref = f"#{index}"
        if index == 1:
            pref = "🥇 "
        if index == 2:
            pref = "🥈 "
        if index == 3:
            pref = "🥉 "
        em.add_field(
            f"**{pref} {username}**", f"**{type.capitalize()}**: {data[user_id]}{suff}"
        )
        index += 1
    await ctx.respond(em)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
