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
plugin = lightbulb.Plugin("AchieveRoles")


@plugin.listener(hikari.MemberUpdateEvent)
async def update(ctx: hikari.MemberUpdateEvent):
    old_roles = ctx.old_member.role_ids
    new_roles = ctx.member.role_ids
    if len(new_roles) <= len(old_roles):
        return
    added_role = [r for r in new_roles if r not in old_roles][0]
    # Server boost role
    if added_role == cfg[cfg["mode"]]["roles"]["boost"]:
        await tools.grant_achievement(ctx.user, "25")
        await tools.add_xp(ctx.user, 200)

    # Color roles
    color_roles = cfg[cfg["mode"]]["roles"]["colors"]
    if added_role in color_roles:
        await tools.grant_achievement(ctx.user, "42")


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
