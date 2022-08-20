import lightbulb
import hikari
import logging
from shiki.utils import db, tools


cfg = tools.load_file('config')
users = db.connect().get_database('shiki').get_collection('users')
plugin = lightbulb.Plugin("UserInit")


@plugin.listener(hikari.ShardReadyEvent)
async def ready_listener(_):
    async for member in plugin.bot.rest.fetch_members(cfg[cfg['mode']]['guild']):
        if member.is_bot:
            continue
        if db.find_document(users, {'_id': member.id}) is None:
            logging.warning(
                f'creating document of user {member.id} ({member.username}#{member.discriminator})')
            db.insert_document(
                users, {'_id': member.id, **cfg['db_defaults']['users']})
            # TODO: Mod [re]assigning


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
