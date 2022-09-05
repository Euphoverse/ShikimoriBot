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
import random
import lightbulb
import hikari
import logging
from shiki.utils import db, tools
import shiki
from pyqiwip2p import AioQiwiP2P
from dotenv import load_dotenv
import os


cfg = tools.load_file('config')
users = db.connect().get_database('shiki').get_collection('users')
plugin = lightbulb.Plugin("QiwiDonate")
_auth_key = os.environ['qiwi_auth_key']


@plugin.command
@lightbulb.option(
    'amount',
    'Сумма которую собираете пожертвовать (в рублях)',
    int,
    required=True,
    min_value=1
)
@lightbulb.command(
    'donate',
    'Пожертвовать нам денег',
    auto_defer=True,
    ephemeral=True
)
@lightbulb.implements(lightbulb.SlashCommand)
async def donate(ctx: lightbulb.SlashContext):
    async with AioQiwiP2P(auth_key=_auth_key) as p2p:
        bill = await p2p.bill(amount=ctx.options.amount, comment='Пожертвование от %s (Shikimori 2.0)' % str(ctx.user), lifetime=10)
        await ctx.respond(embed=hikari.Embed(
            title='Пожертвовать %s рублей' % ctx.options.amount,
            description='Нажмите на надпись выше чтобы оплатить счёт! Каждая копейка нам очень поможет!',
            color=shiki.Colors.WAIT,
            url=bill.pay_url
        ))
        while True:
            await asyncio.sleep(4)
            u = await p2p.check(bill.bill_id)

            if u.status == 'WAITING':
                continue

            if u.status == 'PAID':
                await ctx.edit_last_response(embed=hikari.Embed(
                    title='Спасибо большое ♡',
                    description='Пожертвование на %s рублей зачитано!' % int(
                        bill.amount),
                    color=shiki.Colors.SPONSOR
                ))
                db.update_document(users, {'_id': ctx.user.id},
                                   {'donated': db.
                                    find_document({'_id': ctx.user.id})['donated'] + int(bill.amount)})
                return

            if u.status in ['REJECTED', 'EXPIRED']:
                await ctx.edit_last_response(embed=hikari.Embed(
                    title='Платёж не удался',
                    description='Платёж был отклонён или просрочен. Пожалуйста попробуйте ещё раз использовать команду /donate amount:%s' % ctx.options.amount,
                    color=shiki.Colors.ERROR
                ))
                return


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
