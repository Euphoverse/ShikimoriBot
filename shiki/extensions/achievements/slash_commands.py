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
import os


cfg = tools.load_data("./settings/config")
achievements = tools.load_data("./settings/achievements")
users = db.connect().get_database(os.environ["db"]).get_collection("users")
stats = db.connect().get_database(os.environ["db"]).get_collection("stats")
plugin = lightbulb.Plugin("AchieveSlashcommands")


@plugin.listener(hikari.GuildMessageCreateEvent)
async def update(ctx: hikari.GuildMessageCreateEvent):
    # '/like' command listener ( DSMonitoring )
    if (
        ctx.author_id == 575776004233232386
        and ctx.message.interaction != None
        and ctx.message.interaction.name == "like"
    ):
        await tools.grant_achievement(ctx.message.interaction.user, "37")

    # '/play' command listener ( Hori )
    if (
        ctx.author_id == 1000700569507352636
        and ctx.message.interaction != None
        and ctx.message.interaction.name == "play"
    ):
        user = ctx.message.interaction.user
        data = db.find_document(stats, {"_id": user.id})
        if data == None:
            return
        data["play_uses"] += 1
        if data["play_uses"] == 1:
            await tools.grant_achievement(ctx.message.interaction.user, "38")
        if data["play_uses"] == 150:
            await tools.grant_achievement(ctx.message.interaction.user, "39")
        db.update_document(stats, {"_id": user.id}, {"play_uses": data["play_uses"]})


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
