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
from datetime import datetime, timedelta
import lightbulb
from lightbulb.ext import tasks
import hikari
from shiki.utils import db, tools
import shiki
from pyqiwip2p import AioQiwiP2P
import os
import logging


_LOG = logging.getLogger('extensions.qiwi.sponsor')
cfg = tools.load_data('./settings/config')
users = db.connect().get_database(os.environ['db']).get_collection('users')
plugin = lightbulb.Plugin("QiwiDonate")
_auth_key = os.environ['qiwi_auth_key']


@plugin.command
@lightbulb.option(
    'duration',
    'На какое время вы хотите оформить подписку',
    required=True,
    choices=(
        hikari.CommandChoice(name='15 дней - 100р.', value='15 дней|100|15'),
        hikari.CommandChoice(name='1 месяц - 200р.', value='1 месяц|200|30'),
        hikari.CommandChoice(name='2 месяца - 380р. (-20р.)', value='2 месяца|380|60'),
        hikari.CommandChoice(name='3 месяца - 550р. (-50р.)', value='3 месяца|550|90'),
        hikari.CommandChoice(name='6 месяцев - 1050р. (-150 рублей)', value='6 месяцев|1050|180')
    )
)
@lightbulb.command(
    'sponsor',
    'Оформить спонсорскую подписку',
    auto_defer=True,
    ephemeral=True
)
@lightbulb.implements(lightbulb.SlashCommand)
async def sponsor(ctx: lightbulb.SlashContext):
    text = ctx.options.duration.split('|')
    cost, text, days = int(text[1]), text[0], int(text[2])

    async with AioQiwiP2P(auth_key=_auth_key) as p2p:
        bill = await p2p.bill(amount=cost, comment='Покупка спонсорской подписки для %s' % str(ctx.user), lifetime=5)
        await ctx.respond(embed=hikari.Embed(
            title='Спонсорская подписка на %s' % text,
            description='Нажмите на надпись выше чтобы оплатить счёт',
            color=shiki.Colors.WAIT,
            url=bill.pay_url
        ))
        while True:
            await asyncio.sleep(4)
            u = await p2p.check(bill.bill_id)

            if u.status == 'WAITING':
                continue

            if u.status == 'PAID':
                asyncio.create_task(tools.grant_achievement(ctx.user, '12'))
                await ctx.respond(embed=hikari.Embed(
                        title='Спасибо большое ♡',
                        description='Ваша спонсорская подписка продлена на %s!' % text,
                        color=shiki.Colors.SPONSOR
                ).set_author(name=str(ctx.user), icon=ctx.user.display_avatar_url.url))
                asyncio.create_task(tools.sponsor_extension(ctx.author, days))
                await plugin.bot.rest.create_message(
                    cfg[cfg['mode']]['channels']['log'],
                    embed=hikari.Embed(
                        title='Продление подписки %s' % ctx.author,
                        description='%s, спасибо большое за продление подписки на ***%s***💙 Подписка этого пользователя кончится %s' % (
                            ctx.author.mention, text, (sponsor['started'] + timedelta(sponsor['duration'])).strftime('%d.%m.%Y')
                        ),
                        color=shiki.Colors.SPONSOR
                    ).set_footer(str(ctx.author), icon=ctx.author.display_avatar_url.url)
                )

                return

            if u.status in ['REJECTED', 'EXPIRED']:
                await ctx.edit_last_response(embed=hikari.Embed(
                    title='Платёж не удался',
                    description='Платёж был отклонён или просрочен. Пожалуйста попробуйте ещё раз использовать команду /donate amount:%s' % ctx.options.amount,
                    color=shiki.Colors.ERROR
                ))
                return


@plugin.listener(hikari.ShardReadyEvent)
async def on_ready(_):
    sponsor_check.start()


@tasks.task(d=1)
async def sponsor_check():
    _LOG.info('starting sponsor checking')

    NOW = datetime.now()
    for u in db.find_document(users, {'sponsor.started': {'$ne': None}}, multiple=True):
        end = u['sponsor']['started'] + timedelta(u['sponsor']['duration'])

        if NOW > end:
            db.update_document(users, {'_id': u['_id']}, {'sponsor':
                cfg['db_defaults']['users']['sponsor']
            })
            dm = await plugin.bot.rest.create_dm_channel(
                u['_id']
            )
            try:
                await plugin.bot.rest.remove_role_from_member(
                    cfg[cfg['mode']]['guild'],
                    u['_id'],
                    cfg[cfg['mode']]['roles']['sponsor']
                )
            except hikari.ForbiddenError:
                # Raises only if user is server owner
                pass
            try:
                await dm.send(
                    embed=hikari.Embed(
                        title='Ваша спонсорская подписка кончилась',
                        description='Вы можете вернуть подписку командой /sponsor на [нашем сервере](https://join.euphoverse.ru). '
                                    'Если вы хотели отказаться от подписке, то пожалуйста расскажите нам почему вы решили это сделать'
                                    ' в этой форме: [нажмите](https://docs.google.com/forms/d/e/1FAIpQLSe5jAoQwX5ZTfAGaoVAd1RQvEsRj6xWiLz4rlINJS2G2rTepA/viewform?usp=pp_url&entry.1800267171={0}%23{1})'.format(
                                        dm.recipient.username,
                                        dm.recipient.discriminator
                                    ),
                        color=shiki.Colors.ERROR
                    )
                )
            except hikari.ForbiddenError:
                _LOG.warning('subscription ended: user %s (%s) disabled dms from server members' % (dm.recipient, u['_id']))            

        for d in (7, 2):
            if (end - NOW).days != d:
                continue

            dm = await plugin.bot.rest.create_dm_channel(
                u['_id']
            )
            try:
                await dm.send(
                    embed=hikari.Embed(
                        title='Спонсорская подписка кончается',
                        description='Ваша спонсорская подписка кончится через %s! Не забудьте продлить её командой /sponsor на [нашем сервере](https:/join.euphoverse.ru)' % (
                            'неделю' if d == 7 else '2 дня'
                        ),
                        color=shiki.Colors.ERROR
                    )
                )
            except hikari.ForbiddenError:
                _LOG.warning('user %s (%s) disabled dms from server members' % (dm.recipient, u['_id']))
                await plugin.bot.rest.create_message(
                    cfg[cfg['mode']]['channels']['actions'],
                    f'{dm.recipient.mention}', embed=hikari.Embed(
                        title='Спонсорская подписка %s' % dm.recipient,
                        description='%s ваша спонсоркая подписка кончится через %s!' % (
                            dm.recipient.mention,
                            'неделю' if d == 7 else '2 дня'
                        ),
                        color=shiki.Colors.ERROR
                    ),
                    user_mentions=True
                )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
