import discord
from discord import app_commands
from discord.ext import commands
from lib.quiz_helper import *
from lib.leaderboard_helper import *

class Select(discord.ui.Select):
    def __init__(self):
        self.theme = None
        options = [
            discord.SelectOption(label="History", emoji="1️⃣", description="Do you know your past?"),
            discord.SelectOption(label="Geography", emoji="2️⃣", description="Do you know your geography?"),
            discord.SelectOption(label="Pop Culture", emoji="3️⃣", description="What about pop culture?"),
            discord.SelectOption(label="Math", emoji="4️⃣", description="Do you know your math?"),
            discord.SelectOption(label="Riddles", emoji="5️⃣", description="Can you answer these riddles?")
        ]
        super().__init__(custom_id="quizSelect", placeholder="Please select only one set of questions", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "History":
            self.theme = "History"
        elif self.values[0] == "Geography":
            self.theme = "Geography"
        elif self.values[0] == "Pop Culture":
            self.theme = "Pop Culture"
        elif self.values[0] == "Math":
            self.theme = "Math"
        elif self.values[0] == "Riddles":
            self.theme = "Riddles"

        questions = load_questions(self.theme)
        if self.theme != "Riddles":
            for i in range(len(questions)):
                em = discord.Embed(title=f"Question {i + 1}", description=questions[i])
                await interaction.response.send_message(embed=em, view=load_view(i, questions, self.theme))
        else:
            correct = 0
            for i in range(len(questions)):
                answer = load_answers(i, self.theme)
                em = discord.Embed(title=f"Question {i + 1}", description=f"{questions[i]}\nPlease type your answer")
                try:
                    await interaction.response.send_message(embed=em)
                except discord.InteractionResponded:
                    await interaction.followup.send(embed=em)

                try:
                    message = await interaction.client.wait_for(
                        'message',
                        timeout=30.0,
                        check=lambda m: m.author == interaction.user and m.channel == interaction.channel
                    )

                    if message.author.bot:
                        return

                    # Check if the answer is correct (case-insensitive)
                    if message.content.lower() == answer.lower():
                        correct += 1
                        increment_correct(interaction.user.id, self.theme)
                        await interaction.followup.send("Answer recorded..")
                
                except TimeoutError:
                    await interaction.followup.send(f"Time's up! Please try again.\nYou got {correct} answers correct!")
                    return

                if i == len(questions) - 1:
                    await interaction.followup.send(f"You got {correct} answers correct!")

class SelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Select())

class Quiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Quiz online")

    quiz = app_commands.Group(name="quiz", description="All the commands related to quiz")

    @quiz.command(name="leaderboard", description="See who has the highest amount of questions correct")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"This command is not finished")

    @app_commands.command(name="quiz", description="Test your knowledge")
    async def quiz(self, interaction: discord.Interaction):
        em = discord.Embed(title="Quiz", description="Are you ready to test your knowledge? Select a theme from the dropdown below", color=interaction.user.color)
        await interaction.response.send_message(embed=em, view=SelectView())

async def setup(bot):
    await bot.add_cog(Quiz(bot))
