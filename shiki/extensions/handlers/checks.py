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
import shiki


cfg = tools.load_data('./settings/config')
plugin = lightbulb.Plugin("HandlersChecks")
emoji_denied = cfg['emojis']['access_denied']


@plugin.listener(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if isinstance(event.exception, lightbulb.MissingRequiredRole):
        await event.context.respond(hikari.ResponseType.MESSAGE_UPDATE, embed=hikari.Embed(
            title='Нет ролей',
            description='Чтобы использовать эту команду вам нужно иметь специальную роль',
            color=shiki.Colors.ERROR
        ).set_footer(text=f'{emoji_denied} Отсутствие разрешения'))
        return

    if isinstance(event.exception, lightbulb.CommandIsOnCooldown):
        await event.context.respond(hikari.ResponseType.MESSAGE_UPDATE, embed=hikari.Embed(
            title='Не так быстро!',
            description=f'Вы можете использовать эту команду снова через {event.exception.retry_after:.1f} s',
            color=shiki.Colors.ERROR
        ).set_footer(text=f'{emoji_denied} Превышение лимитов'))
        return

    await event.context.respond(hikari.ResponseType.MESSAGE_UPDATE, embed=hikari.Embed(
            color=shiki.Colors.ERROR
        ).set_author(name='Офицальный сервер', url='https://discord.gg/3s7mnTm9Xt')
         .set_footer(text=f'{emoji_denied} Ошибка')
         .add_field('Получена неизвестная ошибка', 'Данные об ошибке были отправлены на сервер разработчиков. Скоро проблема будет решена')
    )
    
    await plugin.bot.rest.create_message(
        channel=cfg[cfg['mode']]['channels']['errors'],
        embed=hikari.Embed(
            color=shiki.Colors.ERROR
        ).set_footer(text=f'{emoji_denied} Ошибка')
         .add_field('Получена неизвестная ошибка', event.exception)
    )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
