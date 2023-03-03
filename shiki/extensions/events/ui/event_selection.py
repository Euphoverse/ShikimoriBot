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

from lightbulb.ext import tungsten
import typing as t
import hikari
import zoneinfo


msk = zoneinfo.ZoneInfo("Europe/Moscow")


class EventsMenu(tungsten.Components):
    def __init__(
        self, callback, events: t.Sequence[hikari.ScheduledEvent], *args, **kwargs
    ):
        self.callback = callback
        self.events = events
        select_menu = [
            tungsten.Option(
                "%s (%s МСК)"
                % (e.name, e.start_time.astimezone(msk).strftime("%d.%m.%Y %H:%M"))
            )
            for e in events
        ]

        kwargs["select_menu"] = tungsten.SelectMenu(
            "Выберите ивент", min_chosen=1, max_chosen=1, options=select_menu
        )

        super().__init__(*args, **kwargs)

    async def select_menu_callback(
        self,
        options: t.List[tungsten.Option],
        indexes: t.List[int],
        interaction: hikari.ComponentInteraction,
    ) -> None:
        await self.callback(self.ctx, self.events[indexes[0]])
