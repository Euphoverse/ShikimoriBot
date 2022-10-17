import miru
import hikari
import shiki
from shiki.utils import tools


cfg = tools.load_data('./settings/config')


class VerificationTest(miru.Modal):
    text = miru.TextInput(label='Введите свой дискорд тег', 
                          style=hikari.TextInputStyle.SHORT,
                          placeholder='#0000',
                          required=True,
                          min_length=5,
                          max_length=5
    )

    async def callback(self, ctx: miru.ModalContext):
        if list(ctx.values.values())[0][1:] != str(ctx.user.discriminator):
            return await ctx.respond(
                embed=hikari.Embed(
                    title='Неверный тег',
                    description='Чтобы пройти верификацию вам нужно ввести свой #тег в открывшемся окне (#%s)' % (
                        ctx.user.discriminator
                    ),
                    color=shiki.Colors.ERROR
                ),
                flags=hikari.MessageFlag.EPHEMERAL
            )
        
        await ctx.member.add_role(
            cfg[cfg['mode']]['roles']['verify']
        )


class Verification(miru.View):
    def __init__(self, *args, **kwargs):
        super().__init__(timeout=None, *args, **kwargs)


    @miru.button(
        label='Верификация',
        style=hikari.ButtonStyle.SUCCESS,
        emoji='✅'
    )
    async def verify_button(self, button: miru.Button, ctx: miru.ViewContext):
        if cfg[cfg['mode']]['roles']['verify'] in ctx.member.role_ids:
            return await ctx.respond(embed=hikari.Embed(
                title='Действие отменено',
                description='Вы уже верифицировались! Начните общение в канале <#%s>' % cfg[cfg['mode']]['channels']['general'],
                color=shiki.Colors.ERROR
            ), flags=hikari.MessageFlag.EPHEMERAL)

        await ctx.respond_with_modal(VerificationTest('Ваш тег: #%s' % ctx.user.discriminator))
