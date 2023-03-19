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

from datetime import datetime, timedelta, timezone
import re
import lightbulb
import hikari
from shiki.utils import db, tools
import time
import os


cfg = tools.load_data("./settings/config")
users = db.connect().get_database(os.environ["db"]).get_collection("users")
plugin = lightbulb.Plugin("QuickMisc")


@plugin.listener(hikari.GuildMessageCreateEvent)
async def message_sent(ctx: hikari.GuildMessageCreateEvent):
    if ctx.author.is_bot:
        return
    if ctx.content == None:
        return
    raw_content = ctx.content.lower()
    if not raw_content.startswith("шики"):
        return
    content = tools.fetch_content(raw_content)

    if content == "msk":
        msk = datetime.now(tz=timezone.utc) + timedelta(hours=3)
        return await ctx.message.respond(msk.strftime("%H:%M:%S"), reply=True)

    if content == "snowflake":
        search = re.search(r"\d+", ctx.content)
        if search is None:
            return await ctx.message.respond(
                "Ты не указал сноуфлек <:4408ganyuinsane:1027509912609239040>",
                reply=True,
            )

        snowflake_id = int(search.group(0))
        snowflake_date = hikari.Snowflake(snowflake_id).created_at
        return await ctx.message.respond(
            f"<t:{round(time.mktime(snowflake_date.timetuple()))}>", reply=True
        )

    if content == "help":
        help_channel = cfg[cfg["mode"]]["channels"]["information"]
        return await ctx.message.respond(
            f"Список быстрых команд находится в канале <#{help_channel}> <a:4426ganyuspinfingers:1027509918783242270>"
        )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
