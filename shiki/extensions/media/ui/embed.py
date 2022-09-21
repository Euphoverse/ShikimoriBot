from datetime import datetime
import hikari
import miru
import shiki
from shiki.utils import db


users = db.connect().get_database('shiki').get_collection('users')


# - Modals

# Editing title, description and URl
class TitleDesc(miru.Modal):
    name = miru.TextInput(
        label="Заголовок",
        placeholder="Введите заголовок сообщения",
        max_length=256, custom_id='title'
    )
    url = miru.TextInput(
        label="Ссылка",
        placeholder="Введите ссылку для заголовка сообщения",
        max_length=256, custom_id='url'
    )
    desc = miru.TextInput(
        label='Описание', placeholder="Введите описание сообщения",
        style=hikari.TextInputStyle.PARAGRAPH,
        max_length=4000, custom_id='description'
    )

    def __init__(self, embed, *args, **kwargs):
        self.embed = embed
        super().__init__(*args, **kwargs)

    async def callback(self, ctx: miru.ModalContext):
        for i in ctx.values:
            if i.custom_id == 'title' and ctx.values[i] != '':
                self.embed.title = ctx.values[i]
            elif i.custom_id == 'description' and ctx.values[i] != '':
                self.embed.description = ctx.values[i]
            elif i.custom_id == 'url' and ctx.values[i] != '':
                self.embed.url = ctx.values[i]
        await ctx.edit_response(embed=self.embed)


# Editing timestamps
class Timestamp(miru.Modal):
    date = miru.TextInput(
        label="Дата",
        value='00.00.0000',
        placeholder="Введите дату в формате ДД.ММ.ГГГГ",
        max_length=10, min_length=10, custom_id='date'
    )
    time = miru.TextInput(
        label="Время",
        value='00:00:00',
        placeholder="Введите время в формате ЧЧ:ММ:СС",
        max_length=8, min_length=8, custom_id='time'
    )

    def __init__(self, embed, *args, **kwargs):
        self.embed = embed
        super().__init__(*args, **kwargs)

    async def callback(self, ctx: miru.ModalContext):
        for i in ctx.values:
            if i.custom_id == 'date':
                date = ctx.values[i]
            elif i.custom_id == 'time':
                time = ctx.values[i]
        self.embed.timestamp = datetime.strptime(
            '%sT%s' % (date, time), '%d.%m.%YT%H:%M:%S'
        ).astimezone()
        await ctx.edit_response(embed=self.embed)


# Editing color
class EditColor(miru.Modal):
    color = miru.TextInput(
        label='HEX Цвет',
        value='#000000',
        placeholder='Введите HEX код цвета (#000000)',
        max_length=7, min_length=7
    )

    def __init__(self, embed, *args, **kwargs):
        self.embed = embed
        super().__init__(*args, **kwargs)

    async def callback(self, ctx: miru.ModalContext) -> None:
        self.embed.color = hikari.Color.from_hex_code(
            list(ctx.values.items())[0])
        await ctx.edit_response(embed=self.embed)


# Editing author
class EditAuthor(miru.Modal):
    name = miru.TextInput(
        label='Имя',
        placeholder='Введите имя автора',
        max_length=256, required=True,
        custom_id='name'
    )
    url = miru.TextInput(
        label='URL',
        placeholder='Введите ссылку',
        custom_id='url'
    )
    icon_url = miru.TextInput(
        label='Иконка автора',
        placeholder='Введите ссылку на иконку автора',
        required=False, custom_id='icon_url'
    )

    def __init__(self, embed, *args, **kwargs):
        self.embed = embed
        super().__init__(*args, **kwargs)

    async def callback(self, ctx: miru.ModalContext) -> None:
        for i in ctx.values:
            if i.custom_id == 'name':
                name = ctx.values[i] if ctx.values[i] != '' else None
            elif i.custom_id == 'icon_url':
                icon_url = ctx.values[i] if ctx.values[i] != '' else None
            elif i.custom_id == 'url':
                url = ctx.values[i] if ctx.values[i] != '' else None
        self.embed.set_author(
            name=name,
            icon=icon_url,
            url=url
        )
        await ctx.edit_response(embed=self.embed)


# - Main view
class EmbedConstructor(miru.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @miru.button(label='Title, Desc., URL')
    async def edit_title(self, button: miru.Button, ctx: miru.ViewContext):
        modal = TitleDesc(ctx.message.embeds[0], 'Заголовок, Описание, Ссылка')
        await ctx.respond_with_modal(modal)

    @miru.select(
        options=[
            miru.SelectOption('Ручная установка', 'timestamp',
                              'Ввести время вручную', emoji='<:color:821446833590894652>'),
            miru.SelectOption('Автоматическая установка', 'now',
                              'Установить нынешнее время автоматически', emoji='🤖')
        ],
        placeholder='Время'
    )
    async def edit_timestamp(self, select: miru.Select, ctx: miru.ViewContext):
        embed = ctx.message.embeds[0]
        if select.values[0] == 'now':
            embed.timestamp = datetime.now().astimezone()
            await ctx.edit_response(
                embed=embed
            )
            return

        modal = Timestamp(ctx.message.embeds[0], 'Установка времени')
        await ctx.respond_with_modal(modal)

    @miru.select(
        options=[miru.SelectOption(
            'Ручная установка', 'manual', 'Ввести HEX цвета вручную', emoji='<:color:821446833590894652>')
        ] + [
            miru.SelectOption(color, color, 'shiki.Colors.%s' % color)
            for color in shiki.Colors.ALL_COLORS
        ],
        placeholder='Цвет'
    )
    async def edit_color(self, select: miru.Select, ctx: miru.ViewContext):
        embed = ctx.message.embeds[0]
        if select.values[0] == 'manual':
            modal = EditColor(embed, 'Изменение цвета')
            await ctx.respond_with_modal(modal)
            return

        embed.color = eval('shiki.Colors.%s' % select.values[0])
        await ctx.edit_response(
            embed=embed
        )

    @miru.select(
        options=[
            miru.SelectOption('Ручная установка', 'manual',
                              'Установить автора вручную', emoji='<:color:821446833590894652>'),
            miru.SelectOption('Автоматическая установка', 'auto',
                              'Установить вас как автора сообщения', emoji='🤖')
        ],
        placeholder='Автор'
    )
    async def edit_author(self, select: miru.Select, ctx: miru.ViewContext):
        embed = ctx.message.embeds[0]
        if select.values[0] == 'manual':
            modal = EditAuthor(embed, 'Изменение автора')
            await ctx.respond_with_modal(modal)

        embed.set_author(
            name=ctx.user.username,
            icon=ctx.user.display_avatar_url.url
        )
        await ctx.edit_response(
            embed=embed
        )

    async def on_timeout(self) -> None:
        try:
            await self.message.fetch_channel()
        except hikari.NotFoundError:
            return
        await self.message.delete()
