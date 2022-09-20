from datetime import datetime
import hikari
import miru
import shiki
from shiki.utils import db


users = db.connect().get_database('shiki').get_collection('users')


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
                              'Ввести время вручную'),
            miru.SelectOption('Автоматическая установка', 'now',
                              'Установить нынешнее время автоматически')
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

    async def on_timeout(self) -> None:
        try:
            await self.message.fetch_channel()
        except hikari.NotFoundError:
            return
        await self.message.delete()
