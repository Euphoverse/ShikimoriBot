import asyncio
from datetime import datetime, timedelta
import lightbulb
import hikari
import logging
from shiki.utils import db, tools
import shiki


cfg = tools.load_file('config')
users = db.connect().get_database('shiki').get_collection('users')
plugin = lightbulb.Plugin("EventsCommands")


@plugin.command
@lightbulb.add_checks(lightbulb.has_roles(cfg[cfg['mode']]['roles']['events_manager']))
@lightbulb.command(
    'events',
    'Команды для управления ивентами',
    auto_defer=True
)
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def events(ctx: lightbulb.SlashContext) -> None:
    # Command group /events
    pass


@events.child
@lightbulb.command(
    'create',
    'Запустить процесс создания нового ивента',
    inherit_checks=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def create(ctx: lightbulb.SlashContext) -> None:
    def check():
        return event.author_id == ctx.user.id and event.channel_id == ctx.channel_id

    # Step 1 - Title
    await ctx.respond(embed=hikari.Embed(
        title='#1 Название ивента',
        description='Напишите название ивента',
        color=shiki.Colors.WAIT
    ))

    while True:
        event = await plugin.bot.wait_for(
            hikari.GuildMessageCreateEvent,
            timeout=30
        )
        if check():
            break
    title = event.message.content
    await event.message.delete()

    # Step 2 - Description
    await ctx.edit_last_response(embed=hikari.Embed(
        title='#2 Описание ивента',
        description='Напишите описание ивента',
        color=shiki.Colors.WAIT
    ))

    while True:
        event = await plugin.bot.wait_for(
            hikari.GuildMessageCreateEvent,
            timeout=30
        )
        if check():
            break
    desc = event.message.content
    await event.message.delete()

    # Step 3 - Channel
    await ctx.edit_last_response(embed=hikari.Embed(
        title='#3 Место проведения',
        description='Отправьте приглашение в голосовой канал',
        color=shiki.Colors.WAIT
    ))

    while True:
        event = await plugin.bot.wait_for(
            hikari.GuildMessageCreateEvent,
            timeout=30
        )
        if check():
            break
    channel = (await plugin.bot.rest.fetch_invite(event.message.content.split('/')[-1])).channel
    await event.message.delete()

    # Step 4 - Host
    await ctx.edit_last_response(embed=hikari.Embed(
        title='#4 Ведущий',
        description='Отправьте пинг ведущего',
        color=shiki.Colors.WAIT
    ))

    while True:
        event = await plugin.bot.wait_for(
            hikari.GuildMessageCreateEvent,
            timeout=30
        )
        if check():
            break
    host = event.message.user_mentions[list(
        event.message.user_mentions.keys())[0]]
    await event.message.delete()

    await ctx.edit_last_response(embed=hikari.Embed(
        title='Почти готово',
        description='Подготавливаю данные и создаю ивент...',
        color=shiki.Colors.WAIT
    ))

    # Generating event
    event = await ctx.app.rest.create_voice_event(
        ctx.guild_id,
        channel,
        title,
        datetime.now() + timedelta(days=1),
        description=desc,
        reason='Event created by %s' % str(ctx.user)
    )

    event_link = 'https://discord.gg/%s?event=%s' % (
        (await plugin.bot.rest.create_invite(channel, unique=False)).code,
        event.id
    )

    embed = hikari.Embed(
        title='Ивент создан',
        description='Название: `%s`\nОписание: `%s`\nКанал: <#%s>\nВедущий: %s' % (
            title, desc, channel.id, host.mention),
        url=event_link,
        color=shiki.Colors.SUCCESS
    )
    embed.set_footer(
        'Для изменения даты проведения ивента измените её в настройках ивента')
    await ctx.edit_last_response(embed=embed)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
