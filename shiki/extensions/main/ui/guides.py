import asyncio
import miru
import hikari
import shiki
from shiki.utils import tools, db
import os


cfg = tools.load_data('./settings/config')
tags = tools.load_data('./settings/tags')
users = db.connect().get_database(os.environ['db']).get_collection('users')


async def role_handler(self, select: miru.Select, ctx: miru.ViewContext):
    r = int(select.values[0])
    if r not in ctx.member.role_ids:
        await ctx.bot.rest.add_role_to_member(
            ctx.guild_id,
            ctx.user.id,
            r
        )
        await ctx.respond(
            flags=hikari.MessageFlag.EPHEMERAL,
            embed=hikari.Embed(
                title='Роль выдана!',
                color=shiki.Colors.SUCCESS
            )
        )
        return
    await ctx.bot.rest.remove_role_from_member(
        ctx.guild_id,
        ctx.user.id,
        r
    )
    await ctx.respond(
        flags=hikari.MessageFlag.EPHEMERAL,
        embed=hikari.Embed(
            title='Роль убрана!',
            color=shiki.Colors.ERROR
        )
    )


async def tag_handler(self, select: miru.Select, ctx: miru.ViewContext):
    t = select.values[0]
    data = db.find_document(users, {'_id': ctx.user.id})

    if t not in data['tags']:
        data['tags'].append(t)
        if t in ["english", "russian", "japanese", "kazakh", "turkish", "ukrainian", "french", "german", "spanish", "polish"]:
            asyncio.create_task(tools.grant_achievement(ctx.user, '51'))
        await ctx.respond(
            flags=hikari.MessageFlag.EPHEMERAL,
            embed=hikari.Embed(
                title='Тег выдан!',
                color=shiki.Colors.SUCCESS
            )
        )
    else:
        data['tags'].remove(t)
        await ctx.respond(
            flags=hikari.MessageFlag.EPHEMERAL,
            embed=hikari.Embed(
                title='Тег убран!',
                color=shiki.Colors.ERROR
            )
        )
    db.update_document(users, {'_id': ctx.user.id}, {'tags': data['tags']})


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
            embeds=[tools.embed_from_dict(e) for e in child['embeds']]
        )
    elif child['type'] == 'sub':
        sp = SubPage(child)
        m = await ctx.respond(flags=hikari.MessageFlag.EPHEMERAL, embeds=[tools.embed_from_dict(e) for e in child['embeds']], components=sp.build())
        await sp.start(m)
    elif child['type'] == 'roles':
        rp = Roles(child)
        m = await ctx.respond(flags=hikari.MessageFlag.EPHEMERAL, embeds=[tools.embed_from_dict(e) for e in child['embeds']], components=rp.build())
        await rp.start(m)
    elif child['type'] == 'tags':
        tp = Tags(child)
        m = await ctx.respond(flags=hikari.MessageFlag.EPHEMERAL, embeds=[tools.embed_from_dict(e) for e in child['embeds']], components=tp.build())
        await tp.start(m)


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


class Roles(miru.View):
    def __init__(self, data: dict) -> None:
        super().__init__(timeout=600)
        self.data = data
        self.children[0].options = [
            miru.SelectOption(
                label=r['name'],
                value=r['id'][cfg['mode']]
            ) if not data['replace_emojis']
            else miru.SelectOption(
                label=r['name'][r['name'].index(' ') + 1:],
                value=r['id'][cfg['mode']],
                emoji=r['name'][:r['name'].index(' ')]
            ) for r in self.data['roles']
        ]
    
    @miru.select(placeholder="Выберите роль", options=[miru.SelectOption('Загрузка...', 'still-loading', 'Роли подгружаются. Пожалуйста подождите...', '🕐')])
    async def topic_select(self, select: miru.Select, ctx: miru.ViewContext):
        await role_handler(self, select, ctx)

    async def on_timeout(self) -> None:
        try:
            await self.message.delete()
        except hikari.NotFoundError:
            pass


class Tags(miru.View):
    def __init__(self, data: dict) -> None:
        super().__init__(timeout=600)
        self.data = data
        self.children[0].options = [
            miru.SelectOption(
                tags[t][tags[t].index(' ') + 1:],
                t,
                emoji=tags[t][:tags[t].index(' ')]
            ) for t in self.data['tags']
        ]
    
    @miru.select(placeholder="Выберите тег", options=[miru.SelectOption('Загрузка...', 'still-loading', 'Роли подгружаются. Пожалуйста подождите...', '🕐')])
    async def topic_select(self, select: miru.Select, ctx: miru.ViewContext):
        await tag_handler(self, select, ctx)

    async def on_timeout(self) -> None:
        try:
            await self.message.delete()
        except hikari.NotFoundError:
            pass