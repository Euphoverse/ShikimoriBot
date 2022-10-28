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
from lightbulb.ext import tasks
from shiki.utils import tools
import hikari
import lightbulb
import dotenv
import os
import logging
import miru


cfg = tools.load_data('./settings/config')
_LOG = logging.getLogger('core.bot')

dotenv.load_dotenv()
bot = lightbulb.BotApp(
    os.environ['test-token'] if cfg['mode'] == 'test' else os.environ['prod-token'],
    intents=hikari.Intents.ALL,
    default_enabled_guilds=cfg[cfg['mode']]['guild'])
if cfg['mode'] == 'test':
    _LOG.warning('Bot is running in test mode!')

for folder in os.listdir('./shiki/extensions'):
    for plugin in filter(lambda x: x.endswith('.py'), os.listdir('./shiki/extensions/%s' % folder)):
        bot.load_extensions('shiki.extensions.%s.%s' % (folder, plugin[:-3]))


def run() -> None:
    if os.name != 'nt':
        import uvloop

        uvloop.install()
    tasks.load(bot)
    miru.load(bot)
    bot.run(activity=hikari.Activity(name='github: Euphoverse/ShikimoriBot'))
