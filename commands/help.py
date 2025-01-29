import discord
from discord import app_commands
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Help Online")

    @app_commands.command(name="help", description="Learn about commands")
    async def help(self, interaction: discord.Interaction):
        em = discord.Embed(title="Help Command", description="These are all the commands", color=interaction.user.color)
        em.add_field(name="Levels", value="Setup - Admins Only\nEdit - Admins Only\nRank - Show your rank\nGive - Admins Only\nRole - Admins Only")
        em.add_field(name="Tickets", value="Setup - Admins Only\nCreate - Create a ticket\nClose - Close your ticket\nDelete - Admins Only")
        em.add_field(name="Quiz", value="Quiz - Test your knowledge\nLeaderboard - Check who has the highest score")
        em.add_field(name="Others", value="Ping - Show the latency of the bot")

        await interaction.response.send_message(embed=em)

async def setup(bot):
    await bot.add_cog(Help(bot))