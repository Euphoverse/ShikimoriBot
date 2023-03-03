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
import lightbulb
import hikari
from shiki.utils import db, tools


cfg = tools.load_data("./settings/config")
posts = tools.load_data("./settings/post_suggestions")
plugin = lightbulb.Plugin("PostSuggestionsCreatePost")


@plugin.listener(hikari.ReactionAddEvent)
async def on_reaction(event: hikari.ReactionAddEvent):
    if event.user_id == plugin.bot.get_me().id:
        return
    for s in posts.values():
        if s["review"][cfg["mode"]] == event.channel_id:
            post = s
            break
    else:  # Runs if loop wasn't breaked
        return

    mg = await plugin.bot.rest.fetch_message(event.channel_id, event.message_id)
    if event.is_for_emoji("🟩"):
        author_id = hikari.Snowflake(mg.content.split("\n")[3].split(" ")[2])
        await plugin.bot.rest.create_message(
            post["post"][cfg["mode"]],
            "`🖌️ %s`\n`👤 Модератор: %s`\n%s"
            % (
                mg.content.split("\n")[2],
                plugin.bot.cache.get_member(mg.content.split("\n")[0], event.user_id),
                "\n".join(mg.content.split("\n")[4:]),
            ),
        )
        await tools.grant_achievement(author_id, "50", plugin.bot.rest)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
