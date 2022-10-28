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

from datetime import datetime
import aiohttp
import hikari
import miru
import shiki
from shiki.utils import db
import os


users = db.connect().get_database(os.environ['db']).get_collection('users')


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
            list(ctx.values.items())[0][1])
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


# Editing footer
class EditFooter(miru.Modal):
    text = miru.TextInput(
        label='Текст',
        placeholder='Введите текст футера',
        required=True, custom_id='text',
        max_length=2048
    )
    icon_url = miru.TextInput(
        label='Иконка автора',
        placeholder='Введите ссылку на иконку автора',
        required=False, custom_id='icon_url'
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
            if i.custom_id == 'text':
                text = ctx.values[i] if ctx.values[i] != '' else None
            elif i.custom_id == 'icon_url':
                icon_url = ctx.values[i] if ctx.values[i] != '' else None
        self.embed.set_footer(
            text,
            icon=icon_url
        )
        await ctx.edit_response(embed=self.embed)


# Editing image
class EditImage(miru.Modal):
    text = miru.TextInput(
        label='URL',
        placeholder='Ссылка на картинку',
        required=True
    )

    def __init__(self, embed, *args, **kwargs):
        self.embed = embed
        super().__init__(*args, **kwargs)

    async def callback(self, ctx: miru.ModalContext) -> None:
        self.embed.set_image(
            image=ctx.values[ctx.values.keys()[0]]
        )
        await ctx.edit_response(embed=self.embed)


# Editing thumbnail
class EditThumbnail(miru.Modal):
    text = miru.TextInput(
        label='URL',
        placeholder='Ссылка на картинку',
        required=True
    )

    def __init__(self, embed, *args, **kwargs):
        self.embed = embed
        super().__init__(*args, **kwargs)

    async def callback(self, ctx: miru.ModalContext) -> None:
        self.embed.set_thumbnail(
            image=ctx.values[ctx.values.keys()[0]]
        )
        await ctx.edit_response(embed=self.embed)


# - Main view
class EmbedConstructor(miru.View):
    def __init__(self, channel, *args, **kwargs):
        self.channel = channel
        super().__init__(*args, **kwargs)

    @miru.button(label='Title, Desc., URL')
    async def edit_title(self, button: miru.Button, ctx: miru.ViewContext, row=0):
        modal = TitleDesc(ctx.message.embeds[0], 'Заголовок, Описание, Ссылка')
        await ctx.respond_with_modal(modal)

    # timestamp
    @miru.button(label='Руч. время', emoji='<:color:821446833590894652>', row=0)
    async def timestamp_manual(self, button: miru.Button, ctx: miru.ViewContext):
        modal = Timestamp(ctx.message.embeds[0], 'Установка времени')
        await ctx.respond_with_modal(modal)

    @miru.button(label='Авт. время', emoji='🤖', row=0)
    async def timestamp_auto(self, button: miru.Button, ctx: miru.ViewContext):
        embed = ctx.message.embeds[0]
        embed.timestamp = datetime.now().astimezone()
        await ctx.edit_response(
            embed=embed
        )

    # author
    @miru.button(label='Руч. автор', emoji='<:color:821446833590894652>', row=0)
    async def author_manual(self, button: miru.Button, ctx: miru.ViewContext):
        modal = EditAuthor(ctx.message.embeds[0], 'Изменение автора')
        await ctx.respond_with_modal(modal)

    @miru.button(label='Авт. автор', emoji='🤖', row=0)
    async def author_auto(self, button: miru.Button, ctx: miru.ViewContext):
        embed = ctx.message.embeds[0]
        embed.set_author(
            name=ctx.user.username,
            icon=ctx.user.display_avatar_url.url
        )
        await ctx.edit_response(
            embed=embed
        )

    # footer
    @miru.button(label='Руч. футер', emoji='<:color:821446833590894652>', row=1)
    async def footer_manual(self, button: miru.Button, ctx: miru.ViewContext):
        modal = EditFooter(ctx.message.embeds[0], 'Изменение футера')
        await ctx.respond_with_modal(modal)

    @miru.button(label='Авт. футер', emoji='🤖', row=1)
    async def footer_auto(self, button: miru.Button, ctx: miru.ViewContext):
        embed = ctx.message.embeds[0]
        embed.set_footer(
            ctx.user.username,
            icon=ctx.user.display_avatar_url.url
        )
        await ctx.edit_response(
            embed=embed
        )

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
                              'Ввести ссылку вручную', emoji='<:color:821446833590894652>'),
        ] + [
            miru.SelectOption('waifu.pics: %s' % c, 'waifupics-%s' % c,
                              'api.waifu.pics/sfw/%s' % c, emoji='<:waifupics:1025748934624293006>')
            for c in ('wink', 'dance', 'cuddle', 'cry', 'hug', 'kiss', 'pat', 'bonk', 'blush', 'smile', 'wave', 'highfive', 'nom', 'happy')
        ],
        placeholder='Изменить картинку'
    )
    async def edit_image(self, select: miru.Select, ctx: miru.ViewContext):
        embed = ctx.message.embeds[0]
        if select.values[0] == 'manual':
            modal = EditImage(embed, 'Изменение картинки')
            await ctx.respond_with_modal(modal)

        params = select.values[0].split('-')

        if params[0] == 'waifupics':
            async with aiohttp.ClientSession(shiki.WAIFUPICS) as s:
                async with s.get('/sfw/%s' % params[-1]) as resp:
                    if resp.status != 200:
                        image_url = None
                    else:
                        image_url = (await resp.json())['url']
        else:
            image_url = None

        embed.set_image(
            image_url
        )
        await ctx.edit_response(
            embed=embed
        )

    @miru.select(
        options=[
            miru.SelectOption('Ручная установка', 'manual',
                              'Ввести ссылку вручную', emoji='<:color:821446833590894652>'),
        ] + [
            miru.SelectOption('waifu.pics: %s' % c, 'waifupics-%s' % c,
                              'api.waifu.pics/sfw/%s' % c, emoji='<:waifupics:1025748934624293006>')
            for c in ('wink', 'dance', 'cuddle', 'cry', 'hug', 'kiss', 'pat', 'bonk', 'blush', 'smile', 'wave', 'highfive', 'nom', 'happy')
        ],
        placeholder='Изменить превью'
    )
    async def edit_thumbnail(self, select: miru.Select, ctx: miru.ViewContext):
        embed = ctx.message.embeds[0]
        if select.values[0] == 'manual':
            modal = EditThumbnail(embed, 'Изменение превью')
            await ctx.respond_with_modal(modal)

        params = select.values[0].split('-')

        if params[0] == 'waifupics':
            async with aiohttp.ClientSession(shiki.WAIFUPICS) as s:
                async with s.get('/sfw/%s' % params[-1]) as resp:
                    if resp.status != 200:
                        image_url = None
                    else:
                        image_url = (await resp.json())['url']
        else:
            image_url = None

        embed.set_thumbnail(
            image_url
        )
        await ctx.edit_response(
            embed=embed
        )

    # send embed
    @miru.button(label='Отправить сообщение', emoji='<a:arrow_up:1025758437625315390>')
    async def done(self, button: miru.Button, ctx: miru.ViewContext):
        await ctx.bot.rest.create_message(
            self.channel,
            embed=ctx.message.embeds[0]
        )
        await ctx.respond(embed=hikari.Embed(
            title='Выполнено',
            description='Сообщение отправлено в канал <#%s>' % self.channel,
            color=shiki.Colors.SUCCESS
        ))

    async def on_timeout(self) -> None:
        try:
            await self.message.fetch_channel()
        except hikari.NotFoundError:
            return
        await self.message.delete()
