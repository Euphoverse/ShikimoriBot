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

import asyncio
from datetime import datetime, timedelta
import random
import lightbulb
import hikari
from shiki.utils import db, tools, embeds
import shiki
import os


cfg = tools.load_data("./settings/config")
users = db.connect().get_database(os.environ["db"]).get_collection("users")
plugin = lightbulb.Plugin("Economy")
currency_emoji = cfg["emojis"]["currency"]
emoji_denied = cfg["emojis"]["access_denied"]


@plugin.command
@lightbulb.command("economy", "Команды связанные с системой экономики", auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def economy(ctx: lightbulb.SlashContext):
    # /economy
    pass


@economy.child
@lightbulb.option("user", "Пользователь", hikari.Member, required=True)
@lightbulb.option("amount", "Сумма", int, required=True, min_value=1)
@lightbulb.command("transfer", "Перевести деньги другому участнику", auto_defer=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def transfer(ctx: lightbulb.SlashContext):
    sender = ctx.author
    recipient = ctx.options.user

    if recipient.is_bot:
        return await ctx.respond(embed=embeds.user_is_bot())

    if sender.id == recipient.id:
        return await ctx.respond(
            embed=hikari.Embed(
                title="Ошибка",
                description="Вы не можете перевести деньги самому себе!",
                color=shiki.Colors.ERROR,
            ).set_footer(text=f"{emoji_denied} Некорректные данные")
        )

    sender_data = db.find_document(users, {"_id": sender.id})
    recipient_data = db.find_document(users, {"_id": recipient.id})

    if sender_data["money"] < ctx.options.amount:
        return await ctx.respond(
            embed=hikari.Embed(
                title="Ошибка",
                description="Вы не можете отправить больше, чем у вас на балансе!",
                color=shiki.Colors.ERROR,
            ).set_footer(text=f"{emoji_denied} Недостаточно средств")
        )

    updated_balance = sender_data["money"] - ctx.options.amount
    db.update_document(users, {"_id": sender.id}, {"money": updated_balance})
    updated_balance = recipient_data["money"] + ctx.options.amount
    db.update_document(users, {"_id": recipient.id}, {"money": updated_balance})

    await ctx.respond(
        embed=hikari.Embed(
            title="Выполнено!",
            description=f"Успешно переведено {ctx.options.amount}{currency_emoji} {recipient.username}!",
            color=shiki.Colors.SUCCESS,
        ).set_footer(
            text=f"Отправитель: {sender.username}", icon=sender.display_avatar_url.url
        )
    )


@economy.child
@lightbulb.add_cooldown(90, 5, lightbulb.UserBucket)
@lightbulb.option(
    "dice", "Номер кости (от 1 до 6)", int, required=True, min_value=1, max_value=6
)
@lightbulb.option("bet", "Ставка", int, required=True, min_value=1)
@lightbulb.command("dice", "Кинуть кости", auto_defer=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def dice(ctx: lightbulb.SlashContext):
    r_dice = random.randint(1, 6)
    user = ctx.author
    user_data = db.find_document(users, {"_id": user.id})
    newbalance = user_data["money"] - ctx.options.bet

    if newbalance < 0:
        await ctx.respond(
            embed=hikari.Embed(
                title="Недостаточно средств",
                description="Вы не можете поставить больше, чем у вас на балансе",
                color=shiki.Colors.ERROR,
            ).set_footer(text=f"{emoji_denied} Недостаточно средств")
        )
        return

    if r_dice == ctx.options.dice:
        # Ставка сыграла
        newbalance += ctx.options.bet * 6
        await ctx.respond(
            embed=hikari.Embed(title="Победа", color=shiki.Colors.SUCCESS)
            .set_footer(
                text=f"{user.username} сыграл в кости", icon=user.display_avatar_url.url
            )
            .add_field(
                f"Вы очень удачливы! Вы выиграли **{ctx.options.bet * 6}**.",
                f"Выпало **{r_dice}**\nВы поставили на **{ctx.options.dice}**",
                inline=False,
            )
        )
    else:
        # Ставка проиграна
        await ctx.respond(
            embed=hikari.Embed(title="Проигрыш", color=shiki.Colors.ERROR)
            .set_footer(
                text=f"{user.username} сыграл в кости", icon=user.display_avatar_url.url
            )
            .add_field(
                f"Увы, ваша ставка не сыграла. Вы проиграли **{ctx.options.bet}**.",
                f"Выпало **{r_dice}**\nВы поставили на **{ctx.options.dice}**",
                inline=False,
            )
        )
    db.update_document(users, {"_id": user.id}, {"money": newbalance})

    if ctx.options.bet >= 1000:
        await tools.add_xp(user, 50)
    else:
        await tools.add_xp(user, 8)


@economy.child
@lightbulb.command("daily", "Получить ежедневный бонус", auto_defer=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def daily(ctx: lightbulb.SlashContext):
    user = ctx.author
    data = db.find_document(users, {"_id": user.id})
    bonus = random.randint(203, 210)
    if data["last_daily"] == 0 or datetime.now() - data["last_daily"] > timedelta(
        days=1
    ):
        db.update_document(
            users,
            {"_id": user.id},
            {"money": data["money"] + bonus, "last_daily": datetime.now()},
        )
        await ctx.respond(
            embed=hikari.Embed(
                title="Бонус",
                description=f"Вы получили свой ежедневный бонус: {bonus}{currency_emoji}.",
                color=shiki.Colors.SUCCESS,
            ).set_footer(text=str(user.username), icon=user.display_avatar_url.url)
        )
        await tools.add_xp(user, 40)
    else:
        time_left = timedelta(days=1) - (datetime.now() - data["last_daily"])
        await ctx.respond(
            embed=hikari.Embed(
                title="Не так быстро!",
                description=f'Ежедневный бонус будет доступен через: {str(time_left).split(".")[0]}.',
                color=shiki.Colors.SUCCESS,
            ).set_footer(text=f"{emoji_denied} Превышение лимитов")
        )


@plugin.listener(hikari.GuildMessageCreateEvent)
async def message_sent(ctx: hikari.GuildMessageCreateEvent):
    user = ctx.author
    if user.is_bot:
        return
    global message_cooldown
    if "message_cooldown" not in globals():
        message_cooldown = []
    if user.id in message_cooldown:
        return
    message_cooldown.append(user.id)
    multiplier = 1
    if ctx.content != None:
        if len(ctx.content) > 15:
            multiplier += 1
        if len(ctx.content) > 50:
            multiplier += 1
    if (
        db.find_document(users, {"_id": user.id}) != None
        and db.find_document(users, {"_id": user.id})["sponsor"] != None
    ):
        multiplier *= 2
    await tools.add_xp(user, random.randint(1, 3) * multiplier)
    await asyncio.sleep(30)
    message_cooldown.remove(user.id)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
