from lightbulb.ext import tungsten
import typing as t
import hikari
import zoneinfo


msk = zoneinfo.ZoneInfo('Europe/Moscow')


class EventsMenu(tungsten.Components):
    def __init__(self, callback, events: t.Sequence[hikari.ScheduledEvent], *args, **kwargs):
        self.callback = callback
        self.events = events
        select_menu = [
            tungsten.Option('%s (%s МСК)' % (
                e.name,
                e.start_time.astimezone(msk).strftime('%d.%m.%Y %H:%M')
            )) for e in events
        ]

        kwargs["select_menu"] = tungsten.SelectMenu(
            "Выберите ивент",
            min_chosen=1,
            max_chosen=1,
            options=select_menu
        )

        super().__init__(*args, **kwargs)

    async def select_menu_callback(
        self,
        options: t.List[tungsten.Option],
        indexes: t.List[int],
        interaction: hikari.ComponentInteraction
    ) -> None:

        await self.callback(self.ctx, self.events[indexes[0]])
