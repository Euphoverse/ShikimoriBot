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
import shiki
from shiki.utils import db, tools


cfg = tools.load_data('./settings/config')
users = db.connect().get_database('shiki').get_collection('users')
plugin = lightbulb.Plugin("MediaBroadcasts")


@plugin.listener(hikari.StartedEvent)
async def get_invites(_):
    global invites
    invites = {}
    for invite in await plugin.bot.rest.fetch_guild_invites(guild=cfg[cfg['mode']]['guild']):
        invites.update({invite.code: invite.uses})


@plugin.listener(hikari.InviteCreateEvent)
async def invite_created(ctx: hikari.InviteCreateEvent):
    invites.update({ctx.invite.code: 0})


@plugin.listener(hikari.InviteDeleteEvent)
async def invite_deleted(ctx: hikari.InviteDeleteEvent):
    del invites[ctx.code]


@plugin.listener(hikari.MemberCreateEvent)
async def member_joined(ctx: hikari.MemberCreateEvent):
    for invite in await plugin.bot.rest.fetch_guild_invites(guild=cfg[cfg['mode']]['guild']):
        if invite.uses != invites[invite.code]:
            inviter = invite.inviter
            data = db.find_document(users, {'_id': inviter.id})['invites']
            db.update_document(users, {'_id': ctx.user_id}, {'invited_by': inviter.id})
            db.update_document(users, {'_id': inviter.id}, {'invites': data + 1})
            await plugin.bot.rest.create_message(
                channel=cfg[cfg['mode']]['channels']['actions'],
                embed=hikari.Embed(
                    title=f'Новый участник',
                    color=shiki.Colors.SUCCESS
                ).set_footer(text=f'Пользователь присоединился', icon=inviter.display_avatar_url.url)
                 .add_field(f'{inviter.username} пригласил пользователя {ctx.user}', f'Приглашений от {inviter.username}: **{data + 1}**')
                )


@plugin.listener(hikari.MemberDeleteEvent)
async def member_left(ctx: hikari.MemberDeleteEvent):
    data = db.find_document(users, {'_id': ctx.user_id})
    inviter, inviter_invites = None, None
    if 'invited_by' in data:
        inviter = ctx.get_guild().get_member(data['invited_by'])
        inviter_data = db.find_document(users, {'_id': data['invited_by']})['invites']
        inviter_invites = inviter_data - 1
        db.update_document(users, {'_id': data['invited_by']}, {'invites': inviter_invites})
    em = hikari.Embed(
        title=f'Участник вышел',
        color=shiki.Colors.ERROR
    )
    if inviter == None:
        em.add_field(f'Пользователь {ctx.user} покинул нас', 'Неизвестно кто его пригласил.')
    else:
        em.add_field(f'Пользователь {ctx.user} покинул нас',
                     f'Его пригласил {inviter.username}.\nИнвайтов у {inviter.username}: {inviter_invites}')
        em.set_footer(text=f'Участник вышел', icon=inviter.display_avatar_url.url)
    await plugin.bot.rest.create_message(
                channel=cfg[cfg['mode']]['channels']['actions'],
                embed=em)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
