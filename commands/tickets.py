import discord
import os
import random
import pymongo

from discord import app_commands
from discord.ext import commands

client = pymongo.MongoClient(os.getenv('mongo_url'))
db = client.tickets

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Tickets Online")

    ticket = app_commands.Group(name="ticket", description="Have an issue? Create a ticket now")

    @ticket.command(name="setup", description="Setup tickets")
    @commands.has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction):
        await interaction.response.send_message("Starting the setup process")

        coll = db.guilds
        guild = coll.find_one({"_id": interaction.guild.id})

        if guild is not None:
            await interaction.followup.send("Ticket has already been setup for this server")
            return

        if not discord.utils.get(interaction.guild.categories, name="OPENED TICKETS"):
            await interaction.guild.create_category(name="OPENED TICKETS")
        if not discord.utils.get(interaction.guild.categories, name="CLOSED TICKETS"):
            await interaction.guild.create_category(name="CLOSED TICKETS")
        if not discord.utils.get(interaction.guild.roles, name="Ticket Master"):
            await interaction.guild.create_role(name="Ticket Master")
        if not discord.utils.get(interaction.guild.channels, name="ticket-logs"):
            await interaction.guild.create_text_channel(name="ticket-logs")

        log_channel = discord.utils.get(interaction.guild.channels, name="ticket-logs")

        coll.insert_one({"_id": interaction.guild.id, "ticket_count": 0, "opened_tickets": [], "closed_tickets": [], "log_channel": log_channel.id})
        await interaction.followup.send("Tickets have been setup. Users can use `/ticket create` in any channel.")

        await log_channel.send("This channel will now be used for ticket logging.")

    @ticket.command(name="create", description="Have an issue? Create a ticket!")
    async def create(self, interaction: discord.Interaction, reason: str):
        # db setup
        coll = db.tickets
        guild_coll = db.guilds

        guild = guild_coll.find_one({"_id": interaction.guild.id})

        if guild is None:
            await interaction.response.send_message("Tickets is not setup for this server...")
            return

        # category stuff & check if user already has a ticket opened
        category: discord.CategoryChannel = discord.utils.get(interaction.guild.categories, name="OPENED TICKETS")
        for ch in category.text_channels:
            if ch.topic == f"{interaction.user.id} DO NOT CHANGE THE TOPIC OF THIS CHANNEL!":
                await interaction.response.send_message(
                    "You already have a ticket open! Ticket located in {0}".format(ch.mention), ephemeral=True)
                return

        # send message to let the user know the bot is doing things
        await interaction.response.send_message("Creating a ticket...")

        # get the ticket number
        ticket_num = guild['ticket_count'] + 1

        # channel settings & create channel
        r1: discord.Role = discord.utils.get(interaction.guild.roles, name="Ticket Master")
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            r1: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel = await category.create_text_channel(
            name=f"ticket-{ticket_num}",
            topic=f"{interaction.user.id} DO NOT CHANGE THE TOPIC OF THIS CHANNEL!",
            overwrites=overwrites
        )

        # insert a collection into the db with info & update the ticket count in db
        coll.insert_one({"_id": interaction.user.id, "ticket_number": ticket_num, "reason": reason, "opened": True, "channel_id": channel.id})
        guild_coll.update_one({"_id": interaction.guild.id}, {"$inc": {"ticket_count": 1}})
        guild_coll.update_one({"_id": interaction.guild.id}, {"$push": {"opened_tickets": ticket_num}})

        # tell the user that their channel was created
        await interaction.followup.send(f"{interaction.user.mention} your ticket has been created. Visit it @ {channel.mention}")

        # create the embed for the ticket & send it in the channel
        ticket_em = discord.Embed(title="Ticket", description=f"{reason}\n\nPlease do not ping any staff. To close this ticket use `/ticket close`", color=interaction.user.color)
        await channel.send(f"Opened by {interaction.user.mention}\n\n{r1.mention}", embed=ticket_em)

        # send a message in the ticket log channel
        ticket_log_id = guild_coll.find_one({"_id": interaction.guild.id})['log_channel']
        ticket_log = interaction.guild.get_channel(ticket_log_id)

        await ticket_log.send(f"A ticket has been opened by {interaction.user.display_name}. The ticket ID is {ticket_num}. Ticket located at {channel.mention}")

    @ticket.command(name="close", description="Close a ticket")
    async def close(self, interaction: discord.Interaction):
        channel = interaction.channel

        # check if the channel is actually a ticket
        if not channel.name.startswith("ticket-"):
            await interaction.response.send_message("This command can only be used in a ticket...")
            return

        # get the ticket number
        split_channel_name = channel.name.split("ticket-")
        ticket = split_channel_name[1]

        # send a message to the user letting them know the ticket is being closed
        await interaction.response.send_message("Attempting to close this ticket...")

        # get the author of the ticket
        ticket_author = channel.topic.split(" ")[0]

        # edit the channel
        category: discord.CategoryChannel = discord.utils.get(interaction.guild.categories, name="CLOSED TICKETS")
        r1: discord.Role = discord.utils.get(interaction.guild.roles, name="Ticket Master")
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            r1: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        await interaction.channel.edit(category=category, overwrites=overwrites)

        # update the db
        ticket_coll = db.tickets
        guild_coll = db.guilds

        ticket_coll.update_one({"_id": int(ticket_author)}, {"$set": {"opened": False}})
        guild_coll.update_one({"_id": interaction.guild.id}, {"$pull": {"opened_tickets": int(ticket)}})
        guild_coll.update_one({"_id": interaction.guild.id}, {"$push": {"closed_tickets": int(ticket)}})

        # tell the user the ticket was closer
        await interaction.followup.send("This ticket was closed")

        # send a message in the log channel
        ticket_log_id = guild_coll.find_one({"_id": interaction.guild.id})['log_channel']
        ticket_log = interaction.guild.get_channel(ticket_log_id)

        await ticket_log.send(f"A ticket has been closed by {interaction.user.display_name}. Ticket ID: {int(ticket)}")

    @ticket.command(name="delete", description="Delete a ticket")
    @commands.has_permissions(manage_messages=True)
    async def delete(self, interaction: discord.Interaction, ticket: int = None):
        channel = interaction.channel

        if not channel.name.startswith('ticket-') and ticket is None:
            await interaction.response.send_message("Please either use this command in a ticket or specify a ticket #.")
            return


        if ticket is None and channel.name.startswith("ticket-"):
            ticket = int(channel.name.split('ticket-')[1])

        # loop through all the channels in the category and check if the name matches the ticket #
        category = discord.utils.get(interaction.guild.categories, name="CLOSED TICKETS")
        for ch in category.text_channels:
            if ch.name == f"ticket-{ticket}":
                await interaction.response.send_message("Deleting the ticket..")

                # Delete the channel
                await ch.delete(reason="Deleted Ticket")

                # update the db
                ticket_coll = db.tickets
                guild_coll = db.guilds
                ticket_author = int(ch.topic.split(" ")[0])

                ticket_coll.delete_one({"_id": ticket_author})
                guild_coll.update_one({"_id": interaction.guild.id}, {"$pull": {"closed_tickets": ticket}})

                # send a message to the log channel
                ticket_log_id = guild_coll.find_one({"_id": interaction.guild.id})['log_channel']
                ticket_log = interaction.guild.get_channel(ticket_log_id)

                await ticket_log.send(f"A ticket has been deleted by {interaction.user.display_name}. Ticket ID is {ticket}")
                return

        await interaction.response.send_message("A ticket could not be found with that ID. It either does not exist or is not closed.")

async def setup(bot):
    await bot.add_cog(Tickets(bot))