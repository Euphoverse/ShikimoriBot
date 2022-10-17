import asyncio
import miru
import hikari
import shiki
from shiki.utils import tools


async def select_handler(self, select: miru.Select, ctx: miru.ViewContext):
    if select.values[0] == 'deselect':
        await ctx.respond('🚫 Выделение убрано', flags=hikari.MessageFlag.EPHEMERAL, delete_after=3)
        return
    if select.values[0] == 'still-loading':
        await ctx.respond(flags=hikari.MessageFlag.EPHEMERAL, embed=hikari.Embed(
            title='Этот компонент загружается',
            description='Бот ещё не закончил настройку этого компонента. Пожалуйста подождите...',
            color=shiki.Colors.ERROR
        ))
        return

    child = self.data['children'][select.values[0]]
    if child['type'] == 'page':
        await ctx.respond(
            flags=hikari.MessageFlag.EPHEMERAL,
            embed=tools.embed_from_dict(child['embed'])
        )
    elif child['type'] == 'sub':
        sp = SubPage(child)
        m = await ctx.respond(flags=hikari.MessageFlag.EPHEMERAL, embed=tools.embed_from_dict(child['embed']), components=sp.build())
        await sp.start(m)


class RootPage(miru.View):
    def __init__(self, name: str) -> None:
        self.data = tools.load_data('./settings/guides', encoding='utf8')[name]
        super().__init__(timeout=None)
        self.children[0].options = [
            miru.SelectOption(self.data['children'][c]['option']['label'], c,
                              emoji=self.data['children'][c]['option']['emoji'])
            for c in self.data['children']
        ] + [miru.SelectOption(
            'Снять выделение',
            'deselect',
            emoji='🚫'
        )]

    @miru.select(placeholder="Выберите раздел", options=[miru.SelectOption('Загрузка...', 'still-loading', 'Гайды подгружаются. Пожалуйста подождите...', '🕐')])
    async def topic_select(self, select: miru.Select, ctx: miru.ViewContext):
        await select_handler(self, select, ctx)


class SubPage(miru.View):
    def __init__(self, data: dict) -> None:
        super().__init__(timeout=600)
        self.data = data
        self.children[0].options = [
            miru.SelectOption(self.data['children'][c]['option']['label'], c,
                              emoji=self.data['children'][c]['option']['emoji'])
            for c in self.data['children']
        ]

    @miru.select(placeholder="Выберите раздел", options=[miru.SelectOption('Загрузка...', 'still-loading', 'Гайды подгружаются. Пожалуйста подождите...', '🕐')])
    async def topic_select(self, select: miru.Select, ctx: miru.ViewContext):
        await select_handler(self, select, ctx)

    async def on_timeout(self) -> None:
        try:
            await self.message.delete()
        except hikari.NotFoundError:
            pass
