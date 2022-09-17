import hikari
import miru
import shiki
from shiki.utils import db


users = db.connect().get_database('shiki').get_collection('users')


class InfoModal(miru.Modal):
    async def callback(self, ctx: miru.ModalContext):
        ...


class EmbedConstructor(miru.View):
    def __init__(self, *args, **kwargs):
        self.embed = hikari.Embed()
        super().__init__(*args, **kwargs)

    ...

    async def on_timeout(self) -> None:
        try:
            await self.message.fetch_channel()
        except hikari.NotFoundError:
            return
        await self.message.delete()
