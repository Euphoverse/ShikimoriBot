import hikari
import miru
import shiki
from shiki.utils import db


users = db.connect().get_database('shiki').get_collection('users')


class InfoModal(miru.Modal):
    info = miru.TextInput(label='Информация о лобби')

    async def callback(self, ctx: miru.ModalContext):
        mg = await ctx.get_channel().fetch_history().last()
        embed = mg.embeds[0]
        embed.description = list(ctx.values.values())[0]
        await mg.edit(embed=embed)
        await ctx.bot.rest.create_message(ctx.channel_id, 'Информация о лобби обновлена', reply=mg)


class ControlView(miru.View):
    def __init__(self, owner_id: int, *args, **kwargs):
        self.owner_id = owner_id
        super().__init__(*args, **kwargs)

    @miru.button(label="Изменить инфо", style=hikari.ButtonStyle.SUCCESS)
    async def edit_info(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        modal = InfoModal('Изменение информации о лобби')
        await ctx.respond_with_modal(modal)

    @miru.button(label="Закрыть лобби", style=hikari.ButtonStyle.DANGER)
    async def basic_button(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        lobbies = db.find_document(users, {'_id': ctx.user.id})['lobbies']
        lobbies.remove(ctx.channel_id)
        db.update_document(users, {'_id': ctx.user.id}, {'lobbies': lobbies})
        await ctx.bot.rest.delete_channel(ctx.channel_id)
        self.stop()

    async def on_timeout(self) -> None:
        try:
            await self.message.fetch_channel()
        except hikari.NotFoundError:
            return
        await self.message.delete()

    async def view_check(self, ctx: miru.ViewContext) -> bool:
        if ctx.user.id != self.owner_id:
            await ctx.respond(embed=hikari.Embed(
                title='Вы не владелец лобби',
                description='Этим меню могут пользоваться только создатель лобби.',
                color=shiki.Colors.ERROR
            ), delete_after=5)
            return False
        return True
