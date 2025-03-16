import discord
from discord import app_commands
from discord.ext import commands

class Whisper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Whisper Online")

    @app_commands.command(name="whisper", description="secretly send someone a message")
    async def whisper(self, interaction: discord.Interaction, user: discord.User, message: str):
        await interaction.response.send_message("Sending message..", ephemeral=True)
        await user.send(f"{interaction.user.mention} has whispered '{message}'")
        await interaction.followup.send("Message sent", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Whisper(bot))