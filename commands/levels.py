import discord
import pymongo
import os
import random
from discord import app_commands
from discord.ext import commands
import asyncio

client = pymongo.MongoClient(os.getenv("mongo_url"))
db = client.levels


class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Levels Online")

    levels = app_commands.Group(name="levels", description="All the leveling commands!")

    @commands.Cog.listener()
    async def on_message(self, message):
        # get the guilds coll
        guilds_coll = db.guilds

        if message.author.bot:
            return

        if message.content.startswith(self.bot.command_prefix):
            return

        if message.guild is None:
            return

        if guilds_coll.find_one({"_id": message.guild.id}) is None or guilds_coll.find_one({"_id": message.guild.id})['disabled'] == True:
            return

        xp_inc = guilds_coll.find_one({"_id": message.guild.id})["xp_inc"]

        # check if user has an account in the db
        coll = db.accounts
        users = coll.find_one({"_id": message.author.id})

        if users is None:
            coll.insert_one({"_id": message.author.id, "xp": xp_inc, "level": 1, "guild": message.guild.id})
        else:
            coll.update_one({"_id": message.author.id}, {"$inc": {"xp": xp_inc}})

        user = coll.find_one({"_id": message.author.id})

        if user['xp'] >= user['level'] * 100:
            coll.update_one({"_id": message.author.id}, {"$inc": {"level": 1}})

            guild_channel = db.guilds.find_one({"_id": message.guild.id})['channel']
            if guild_channel is None:
                await message.guild.owner.send(f"There is an issue with leveling! User: {message.author.id} has leveled up but no log channel is set..")
            else:
                channel = message.guild.get_channel(guild_channel)

                await channel.send(f"{message.author.display_name} has reached level {user['level']}!")

        if user['level'] == 50 or user['level'] == 100:
            await message.guild.owner.send(f"{message.author.display_name} has reached level 50 or 100!")

    @levels.command(name="setup", description='Set the levels channel')
    @commands.has_permissions(manage_messages=True)
    async def setup(self, interaction: discord.Interaction, channel: discord.TextChannel = None, xp: int = None):
        if channel == None:
            channel = interaction.channel

        if xp is None:
            xp = 5

        await interaction.response.send_message(f"Starting the setup process")

        coll = db.guilds
        coll.insert_one({"_id": interaction.guild.id, "channel": channel.id, "xp_inc": xp, "disabled": False})

        await interaction.followup.send(f"The channel set for levels logging is <#{channel.id}>\nThe xp increment is {xp}")

    @levels.command(name='edit', description='Edit the current config')
    @commands.has_permissions(manage_messages=True)
    async def edit(self, interaction: discord.Interaction, channel: discord.TextChannel = None, xp: int = None, disabled: bool = None):
        if channel == None:
            channel = interaction.channel

        if xp is None:
            xp = 5

        if disabled is None:
            disabled = False

        await interaction.response.send_message(f"Editing the current config...")

        coll = db.guilds
        guild = coll.find_one({"_id": interaction.guild.id})

        if guild is None:
            await interaction.followup.send("The guilds is not currently setup for leveling")
            return

        coll.update_one({"_id": interaction.guild.id}, {"$set": {"channel": channel.id, "xp_inc": xp, "disabled": disabled}})

        await interaction.followup.send(f"Current channel: <#{channel.id}>\nXP is: {xp}\nAre levels disabled? {disabled}")

    @levels.command(name="rank", description='Show your current level and xp!')
    async def rank(self, interaction: discord.Interaction, member: discord.Member = None):
        if member is None:
            member = interaction.user

        user_coll = db.accounts
        guild_coll = db.guilds

        user = user_coll.find_one({"_id": member.id})
        guild = guild_coll.find_one({"_id": interaction.guild.id})

        if user is None:
            await interaction.response.send_message("This user hasn't sent a message! They don't have a rank.")
            return

        em = discord.Embed(title="Rank", description=f"{member.display_name}'s current rank is...", color=member.color)
        em.add_field(name="Level", value=user['level'], inline=False)
        em.add_field(name='XP', value=user['xp'], inline=False)
        em.add_field(name='XP required to level up', value=f"{(user['level'] * 100) - user['xp']}", inline=False)
        em.add_field(name='Disabled?', value=guild['disabled'])

        await interaction.response.send_message(embed=em)

    # @levels.command(name='leaderboard', description='View the servers leaderboard')
    # async def leaderboard(self, interaction: discord.Interaction):
    #     guild_coll = db.guilds
    #     users_coll = db.accounts
    #
    #     users = users_coll.find({})
    #
    #     for user in users:
    #         pass
    #
    #     em = discord.Embed(title='Leaderboard', description='View the people with the highest XP')
    #
    #
    #     await interaction.response.send_message("This command is currently under development...")


async def setup(bot):
    await bot.add_cog(Levels(bot))
