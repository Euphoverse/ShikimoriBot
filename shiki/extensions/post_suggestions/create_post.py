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


cfg = tools.load_data("./settings/config")
posts = tools.load_data("./settings/post_suggestions")
plugin = lightbulb.Plugin("PostSuggestionsCreatePost")


@plugin.listener(hikari.MessageCreateEvent)
async def on_message(event: hikari.MessageCreateEvent):
    if event.author_id == plugin.bot.get_me().id:
        return
    for s in posts.values():
        if s["post"][cfg["mode"]] == event.channel_id:
            post = s
            break
    else:  # Runs if loop wasn't breaked
        return
    mg = event.message
    await mg.delete()
    if post["type"] == "message":
        result = []
        if (
            "image" in post["content_types"]
            or "video" in post["content_types"]
            or "any_file" in post["content_types"]
        ) and len(mg.attachments) != 0:
            if "any_file" not in post["content_types"]:
                valid_att = [
                    a.url
                    for a in mg.attachments
                    if any(t in a.media_type for t in post["content_types"])
                ]
            else:
                valid_att = [a.url for a in mg.attachments]

            if len(valid_att) != 0:
                result.extend(valid_att)

        if "text" in post["content_types"] and mg.content is not None:
            result.append(mg.content)

        if "link" in post["content_types"] and (
            mg.content is not None and mg.content.startswith("http")
        ):
            result.append(mg.content)

        if len(result) == 0:
            return

        nmg = await plugin.bot.rest.create_message(
            post["review"][cfg["mode"]],
            "%s\nНовый пост в предложке <#%s>\nАвтор: %s\nID Автора: %s\n%s"
            % (
                mg.guild_id,
                post["post"][cfg["mode"]],
                event.author,
                event.author_id,
                "\n".join(result),
            ),
        )

        await nmg.add_reaction("🟩")


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
