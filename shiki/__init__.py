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

__productname__ = "ShikimoriBot"
__version__ = "2.0.0a"
__description__ = "Discord bot coded specially for Euphoverse Discord server"
__url__ = "https://github.com/JustLian/ShikimoriBot"
__license__ = "BSD-3-Clause"

# API urls
WAIFUPICS = 'https://api.waifu.pics'


# Color palette
class Colors:
    ALL_COLORS = ['SUCCESS', 'ERROR', 'WARNING',
                  'WAIT', 'SPONSOR', 'ANC_HIGH',
                  'ANC_LOW']

    from hikari import Color
    SUCCESS = Color.from_hex_code('#f4c0e6')
    ERROR = Color.from_hex_code('#936cab')
    WARNING = Color.from_hex_code('#a14e7e')
    WAIT = Color.from_hex_code('#c0c1cb')
    SPONSOR = Color.from_hex_code('#95f9e3')
    ACHIEVEMENT = Color.from_hex_code('#c799ff')

    ANC_HIGH = Color.from_hex_code('#85005f')
    ANC_LOW = Color.from_hex_code('#a2a5ff')


IMAGES = {
    'thinking': [
        'https://i.postimg.cc/gkdj26fd/image-2022-09-18-144207362.png'
    ],
    'angry': [
        'https://i.postimg.cc/66CVPnrN/tumblr-634f81dd0aeb75229b16b7c3374fbf22-695744b4-540-1.gif'
    ]
}
