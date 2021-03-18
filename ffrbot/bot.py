import asyncio
import logging
import time

import discord
from discord.ext import commands


from .cogs.racing.races import Races
from .cogs.roles import Roles
from .cogs.core import Core
from .cogs.voting.polls import Polls
from .cogs.rng import RNG
from .cogs.users import Users


from ffrbot.cogs.config import ConfigCommands
from .common import config, constants
from .common.redis_client import RedisClient


def main():
    # format logging
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    db = RedisClient()

    intents = discord.Intents.default()
    intents.members = True

    description = "FFR discord bot"

    bot = commands.Bot(
        command_prefix="?",
        description=description,
        case_insensitive=True,
        intents=intents,
    )

    config.init(db, bot)
    logging.info("initializing bot.")

    bot.add_cog(Core(bot, db))
    bot.add_cog(Races(bot, db))
    bot.add_cog(Roles(bot, db))
    bot.add_cog(Polls(bot, db))
    bot.add_cog(RNG(bot))
    bot.add_cog(Users(bot, db))
    bot.add_cog(ConfigCommands(bot))

    @bot.event
    async def on_ready():
        logging.info("discord.py version: " + discord.__version__)
        logging.info("Logged in as")
        logging.info(bot.user.name)
        logging.info(bot.user.id)
        logging.info("------")

    @bot.event
    async def on_command_completion(ctx: commands.Context):
        msg: discord.Message = ctx.message

        try:
            await msg.add_reaction("✔")
        except Exception as e:
            logging.debug(
                f"on_command_completion exception: {repr(e)},"
                f" original command possibly deleted"
            )

    @bot.event
    async def on_command_error(
        ctx: commands.Context, error: commands.CommandError
    ):
        msg: discord.Message = ctx.message
        logging.warning("command error: " + str(error))
        try:
            await msg.add_reaction("✖")
        except Exception as e:
            logging.debug(
                f"on_command_error exception: {repr(e)},"
                f" original command possibly deleted"
            )

    def handle_exit(client, loop):
        # taken from https://stackoverflow.com/a/50981577
        loop.run_until_complete(client.logout())
        for t in asyncio.Task.all_tasks(loop=loop):
            if t.done():
                t.exception()
                continue
            t.cancel()
            try:
                loop.run_until_complete(asyncio.wait_for(t, 5, loop=loop))
                t.exception()
            except asyncio.InvalidStateError:
                pass
            except asyncio.TimeoutError:
                pass
            except asyncio.CancelledError:
                pass

    def run_client(client, *args, **kwargs):
        loop = asyncio.get_event_loop()
        while True:
            try:
                logging.info("Starting connection")
                loop.run_until_complete(client.start(*args, **kwargs))
            except KeyboardInterrupt:
                handle_exit(client, loop)
                client.loop.close()
                logging.info("Program ended")
                break
            except Exception as e:
                logging.exception(e)
                handle_exit(client, loop)
            logging.info("Waiting until restart")
            time.sleep(constants.Sleep_Time)

    with open("ffrbot/token.txt", "r") as f:
        token = f.read()
    token = token.strip()

    run_client(bot, token)
