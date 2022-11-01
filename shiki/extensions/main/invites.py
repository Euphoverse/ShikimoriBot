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
import shiki
from shiki.utils import db, tools
import os


cfg = tools.load_data('./settings/config')
users = db.connect().get_database(os.environ['db']).get_collection('users')
stats = db.connect().get_database(os.environ['db']).get_collection('stats')
plugin = lightbulb.Plugin("MediaBroadcasts")


@plugin.listener(hikari.StartedEvent)
async def get_invites(_):
    global fetching_invites
    fetching_invites = False
    global invites
    invites = {}
    for invite in await plugin.bot.rest.fetch_guild_invites(guild=cfg[cfg['mode']]['guild']):
        invites.update({invite.code: {"uses": invite.uses, "code_creator": invite.inviter.id}})


@plugin.listener(hikari.InviteCreateEvent)
async def invite_created(ctx: hikari.InviteCreateEvent):
    invites.update({ctx.invite.code: {"uses": ctx.invite.uses, "code_creator": ctx.invite.inviter.id}})


@plugin.listener(hikari.InviteDeleteEvent)
async def invite_deleted(ctx: hikari.InviteDeleteEvent):
    invites[ctx.code]['uses'] = -10
    while fetching_invites:
        await asyncio.sleep(1)
    del invites[ctx.code]


@plugin.listener(hikari.MemberCreateEvent)
async def member_joined(ctx: hikari.MemberCreateEvent):
    global fetching_invites, invites
    fetching_invites = True
    for invite in await plugin.bot.rest.fetch_guild_invites(guild=cfg[cfg['mode']]['guild']):
        if invite.uses != invites[invite.code]['uses']:
            inviter = invite.inviter
            invites[invite.code]['uses'] = invite.uses
            await update_invites(inviter, ctx)
            return
    for key in invites:
        invite = invites[key]
        if(invite['uses'] < 0):
            inviter = ctx.get_guild().get_member(invite['code_creator'])
            await update_invites(inviter, ctx)
            return
    fetching_invites = False



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


async def update_invites(inviter, ctx):
    global fetching_invites
    data = db.find_document(users, {'_id': inviter.id})
    data2 = db.find_document(stats, {'_id': inviter.id})
    data['invites'] += 1
    if data['invites'] == 2: 
        asyncio.create_task(tools.grant_achievement(inviter, '13'))
    if data['invites'] == 5: 
        asyncio.create_task(tools.grant_achievement(inviter, '14'))
    if data['invites'] == 15: 
        asyncio.create_task(tools.grant_achievement(inviter, '15'))
    if data['invites'] == 30: 
        asyncio.create_task(tools.grant_achievement(inviter, '16'))
    if data['invites'] == 100: 
        asyncio.create_task(tools.grant_achievement(inviter, '17'))
    if data['invites'] > data2['invites_claimed']:
        data2['invites_claimed'] = data['invites']
        if data['invites'] % 5 == 0:
            data['money'] += 50 * data['invites']
            asyncio.create_task(tools.sponsor_extension(inviter, 5))
        await tools.add_xp(inviter, 10)
        db.update_document(stats, {'_id': inviter.id}, data2)
    db.update_document(users, {'_id': ctx.user_id}, {'invited_by': inviter.id})
    db.update_document(users, {'_id': inviter.id}, data)
    fetching_invites = False
    await plugin.bot.rest.create_message(
        channel=cfg[cfg['mode']]['channels']['actions'],
        embed=hikari.Embed(
            title=f'Новый участник',
            color=shiki.Colors.SUCCESS
        ).set_footer(text=f'Пользователь присоединился', icon=inviter.display_avatar_url.url)
         .add_field(f'{inviter.username} пригласил пользователя {ctx.user}', f'Приглашений от {inviter.username}: **{data["invites"]}**')
    )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
