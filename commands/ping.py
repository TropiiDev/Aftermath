import discord
import os
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands

load_dotenv()

class ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ping Online")

    @app_commands.command(name="ping", description="Pong!")
    async def ping(self, interaction: discord.Interaction):
        print("Ping Ping Ping")
        await interaction.response.send_message(f":ping_pong:**Pong!**\nLatency: {round(self.bot.latency * 1000)}ms")

async def setup(bot):
    await bot.add_cog(ping(bot))