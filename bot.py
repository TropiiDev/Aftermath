# pip install imports
import discord
from discord.ext import commands

from dotenv import load_dotenv
import asyncio
# import pymongo

# sys imports
import os
import logging
import logging.handlers

load_dotenv()

# sentry.io
import sentry_sdk
sentry_sdk.init(
    dsn=os.getenv("sentry_key"),

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)

# startup stuff
load_dotenv()

intents = discord.Intents().default()
intents.message_content = True
intents.guilds = True
intents.members = True


# create the bot
class MyBot(commands.Bot):
    def __init__(self):
        # super().__init__(command_prefix=get_server_prefix, intents = intents) - prefix setup
        super().__init__(command_prefix="!", intents=intents)
        self.synced = False
        # self.remove_command("help")     

    async def setup_hook(self):
        print(f'\33[32mLogged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def load_extensions(self):
        for name in os.listdir('./commands'):
            if name.endswith('.py'):
                await self.load_extension(f'commands.{name[:-3]}')

    # async def on_ready(self):
    #    await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=""))


# making var for commands in this file
bot = MyBot()
tree = bot.tree


# start bot
async def main():
    async with bot:
        await bot.load_extensions()
        await bot.start(os.getenv("token"))
        await asyncio.sleep(0.1)
    await asyncio.sleep(0.1)


asyncio.run(main())