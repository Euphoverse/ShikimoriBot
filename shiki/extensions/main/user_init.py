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
import os


cfg = tools.load_data('./settings/config')
users = db.connect().get_database(os.environ['db']).get_collection('users')
stats = db.connect().get_database(os.environ['db']).get_collection('stats')
plugin = lightbulb.Plugin("UserInit")
_LOG = logging.getLogger('extensions.main.user_init')


@plugin.listener(hikari.ShardReadyEvent)
async def ready_listener(_):
    async for member in plugin.bot.rest.fetch_members(cfg[cfg['mode']]['guild']):
        if member.is_bot:
            continue
        data = db.find_document(users, {'_id': member.id})
        if data is None:
            _LOG.warning(
                f'creating user document of user {member.id} ({member})')
            db.insert_document(
                users, {'_id': member.id, **cfg['db_defaults']['users']})
        else:
            for key in cfg['db_defaults']['users'].keys():
                if key not in data:
                    _LOG.warning(
                        'missing key "%s" in stats document of user %s (%s)' % (key, str(member), str(member.id)))
                    db.update_document(users, {'_id': member.id}, {
                                       key: cfg['db_defaults']['users'][key]})
        data = db.find_document(stats, {'_id': member.id})
        if data is None:
            _LOG.warning(
                f'creating stats document of user {member.id} ({member})')
            db.insert_document(
                stats, {'_id': member.id, **cfg['db_defaults']['stats']})
        else:
            for key in cfg['db_defaults']['stats'].keys():
                if key not in data:
                    _LOG.warning(
                        'missing key "%s" in stats document of user %s (%s)' % (key, str(member), str(member.id)))
                    db.update_document(stats, {'_id': member.id}, {
                                       key: cfg['db_defaults']['stats'][key]})


@plugin.listener(hikari.MemberCreateEvent)
async def member_join(event: hikari.MemberCreateEvent):
    if event.member.guild_id != cfg[cfg['mode']]['guild']:
        return

    if db.find_document(users, {'_id': event.member.id}) is None:
        db.insert_document(
            users, {'_id': event.member.id, **cfg['db_defaults']['users']})
        db.insert_document(
            stats, {'_id': event.member.id, **cfg['db_defaults']['stats']})
        await event.member.get_guild()\
            .get_channel(cfg[cfg['mode']]['channels']['mods_only'])\
            .send(f'<@&{cfg[cfg["mode"]]["roles"]["mod"]}> {event.member} (<@{event.member.id}>)')
        return

    # User re-joined
    await tools.grant_achievement(event.user, '4')
    await event.member.add_role(
        cfg[cfg['mode']]['roles']['verify']
    )
    await event.member.get_guild()\
        .get_channel(cfg[cfg['mode']]['channels']['general'])\
        .send(f"С возвращением на наш сервер, %s! :>" % (
            event.member.mention
        ))


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
