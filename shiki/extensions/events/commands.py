from datetime import datetime, timedelta, timezone
import zoneinfo
import lightbulb
import hikari
from shiki.utils import db, tools
import shiki
from .ui.event_selection import EventsMenu
import aiohttp


WAIFUPICS = 'https://api.waifu.pics'
msk = zoneinfo.ZoneInfo('Europe/Moscow')
local_tz = datetime.now(timezone.utc).astimezone().tzinfo

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

    if not event.message.content.startswith('https://discord.gg/'):
        await ctx.edit_last_response(embed=hikari.Embed(
            title='Некорректное приглашение',
            description='Вы отправили некорректное приглашение все приглашения должны начинаться с "https://discord.gg/"',
            color=shiki.Colors.ERROR
        ))
        return

    try:
        channel = (await plugin.bot.rest.fetch_invite(event.message.content.split('/')[-1])).channel
    except hikari.NotFoundError:
        await ctx.edit_last_response(embed=hikari.Embed(
            title='Неизвестное приглашение',
            description='Вы отправили нерабочее приглашение',
            color=shiki.Colors.ERROR
        ))
        return
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

    if len(event.message.user_mentions) == 0:
        await ctx.edit_last_response(embed=hikari.Embed(
            title='Ошибка',
            description='Вы не упомянули ни одного пользователя в вашем сообщении',
            color=shiki.Colors.ERROR
        ))
        return
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
        description=desc + '\n\n Ведущий: %s' % str(host),
        reason='Event created by %s' % str(ctx.user)
    )

    event_link = 'https://discord.gg/%s?event=%s' % (
        (await plugin.bot.rest.create_invite(channel, unique=False)).code,
        event.id
    )

    # Saving data to DB
    events_data = tools.load_data('events')
    events_data[str(event.id)] = {
        'title': title,
        'description': desc,
        'host': host.id,
        'channel': channel.id,
        'date': event.start_time.strftime(cfg['time_format']),
        'link': event_link
    }
    tools.update_data('events', events_data)

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


async def announce_callback(ctx: lightbulb.SlashContext, event: hikari.ScheduledEvent):
    async with aiohttp.ClientSession(WAIFUPICS) as s:
        async with s.get('/sfw/happy') as resp:
            if resp.status != 200:
                image_url = None
            else:
                image_url = (await resp.json())['url']
    link = tools.load_data('events')[str(event.id)]['link']
    date = event.start_time.astimezone(msk)
    embed = hikari.Embed(
        title='Ивент %s' % event.name,
        description='Привет всем! %s в %s по МСК пройдёт ивент %s. Не забудьте подписаться на [уведомления об этом ивенте](%s) если планируете прийти!' % (
            date.strftime('%d.%m'),
            date.strftime('%H:%M'),
            event.name,
            link
        ),
        color=shiki.Colors.ANC_HIGH,
        timestamp=datetime.now(local_tz)
    )
    embed.set_image(image_url)
    embed.set_footer(str(ctx.user), icon=ctx.user.display_avatar_url.url)
    await plugin.bot.rest.create_message(
        cfg[cfg['mode']]['channels']['announcements'],
        embed=embed
    )
    await plugin.bot.rest.create_message(
        cfg[cfg['mode']]['channels']['announcements'],
        content='%s %s' % (
            link,
            '' if not ctx.options.role else ctx.options.role.mention
        )
    )
    await ctx.edit_last_response(embed=hikari.Embed(
        title='Готово!',
        description='Объявление успешно отправлено',
        color=shiki.Colors.SUCCESS
    ), components=None)


@events.child
@lightbulb.option(
    'role',
    'Роль которую необходимо упомянуть',
    hikari.Role,
    required=False,
    default=None
)
@lightbulb.command(
    'announce',
    'Создать объявление о запланированном ивенте',
    inherit_checks=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def announce(ctx: lightbulb.SlashContext):
    events = await plugin.bot.rest.fetch_scheduled_events(ctx.guild_id)
    if len(events) == 0:
        await ctx.respond(embed=hikari.Embed(
            title='Нет ивентов',
            description='На этом сервере нет запланированных ивентов',
            color=shiki.Colors.ERROR
        ))
        return
    embed = hikari.Embed(
        title='Выберите ивент',
        color=shiki.Colors.WAIT
    )
    menu = EventsMenu(announce_callback, events, ctx)
    resp = await ctx.respond(embed, components=menu.build())
    await menu.run(resp)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
