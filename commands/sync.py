import discord
from discord.ext import commands


class Sync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Sync Online")

    @commands.command(name="sync", description="Syncs all of the slash commands")
    @commands.is_owner()
    async def sync(self, ctx):
        await self.bot.tree.sync()
        await ctx.send("Synced!")

async def setup(bot):
    await bot.add_cog(Sync(bot))