import discord
import random
from lib.leaderboard_helper import *

def load_questions(theme):
    questions = []
    if theme == "History":
        questions = [
            "When did the second world war start (based on allied views)?",
            "When did the second world war end?",
            "Which of these was one of the superpowers in the cold war?",
            "Who was the loader of North Korea in 1945?",
            "Which country here gained independence between 1945 and 1950?",
            "When was the first Punic War?",
            "Who was the leader of the Soviet Union in 1957?",
            "Who was the leader of the United States in 1966?",
            "What combat method was used by the Vietnam in the Vietnam war?",
            "What was the 1st Reich?",
            "Which battle defeated Harald Hardrada of Norway in 1066?",
            "Approximately how many people died in World War 2?",
            "What ideology was Hungary in 1919?",
            "Who developed the ideology of Communism?",
            "What happened in Tiananmen Square?"
        ]
    elif theme == "Geography":
        questions = [
            "Name which continent Kenya is on.",
            "What is an Oxbow lake?",
            "What happens to the coast when water interacts with it?",
            "What is the capital of El Salvador?",
            "What is the longest river in the world?",
            'What country is known as "Land of a Thousand Lakes"?',
            "What is the tallest mountain in the world?",
            "What is the most isolated place on the world called?",
            "How many bodies of water is the Great Lakes made of?",
            "What is the 6th most populated country in the world?",
            "What is the capital city of Malta?",
            'Which of the following is a "wonder of the world"?',
            "What is the smallest Country in the world?",
            "What is the smallest US state?",
            "What is the most populated city in the world?"
        ]

    return questions

def load_answers(question, theme):
    answers = []
    if theme == "History":
        answers = [
            '0 1939',
            '1 1945',
            '2 USA,USSR',
            '3 Terentii Shtykov,Kim Il-Sung',
            '4 Vietnam,Indonesia,Philippines,Jordan,India,Pakistan,Myanmar,SriLanka (Ceylon),Israel,Laos,Cambodia,Syria',
            '5 264 BC - 241 BC',
            '6 Nikita Khrushchev',
            '7 Lyndon B Johnson',
            '8 Guerrilla Warfare',
            '9 Holy Roman Empire',
            '10 Battle of Stamford Bridge',
            '11 70 - 85 million',
            '12 Communist',
            '13 Karl Marx',
            '14 Nothing,Massacre'
        ]
    elif theme == "Geography":
        answers = [
            "0 Africa",
            "1 A curved lake formed from a horseshoe",
            "2 Erosion",
            "3 San Salvador",
            "4 Nile",
            "5 Finland",
            "6 Mount Everest",
            "7 Point Nemo",
            "8 5",
            "9 Nigeria",
            "10 Valletta",
            "11 The Great Wall of China,Petra,Christ the Redeemer,Machu Picchu,Chichen Itza,The Colosseum and The Taj Mahal",
            "12 Vatican City",
            "13 Rhode Island",
            "14 Tokyo"
        ]

    answer = answers[question]
    if ',' in answer:
        only_answer = answer.split(f"{str(question)} ")[1]
        possible_answers = only_answer.split(',')
        return possible_answers
    else:
        return answer.split(f"{str(question)} ")[1]

def load_choices(question, theme):
    choices = []
    if theme == "History":
        choices = [
            '0 1940,1938,1914',
            '1 1946,1944,1918,1920',
            '2 China,The UK,Germany',
            '3 Syngman Rhee,Chiang Kai-shek,Kim Jong Un',
            '4 Bahrain,Canada,Australia',
            '5 300 BC - 200 BC,264 BC - 146 BC,120 BC -116 BC',
            '6 Leonid Brezhnev,Joseph Stalin,Mikhail Gorbachev',
            '7 John F. Kennedy,Dwight D. Eisenhower,Richard Nixon',
            '8 Air Strikes,Nuclear Warfare,Hand-to-Hand Combat',
            '9 Byzantine Empire,Ottoman Empire,Russian Empire',
            '10 Battle of Hastings,Battle of Waterloo,Battle of Gettysburg',
            '11 100 - 120 million,15 to 30 million,30 to 45 million',
            '12 Capitalist,Monarchist,Fascist',
            '13 Vladimir Lenin,Joseph Stalin,Friedrich Engels',
            '14 The Fall of the Great Wall of China,A Soccer/Football Match,The signing of the Magna Carta'
        ]
    elif theme == "Geography":
        choices = [
            "0 South America,Europe,Asia",
            "1 A circular river,A triangle-shaped lake,A square-shaped lake",
            "2 Freezing,Glaciation,Transpiration",
            "3 Lima,Caracas,Bogota",
            "4 Amazon River,Yangtze River,Mississippi River",
            "5 Norway,Switzerland,Sweden",
            "6 Mount Fuji,Mount Kilimanjaro,Mount Vesuvius",
            "7 Bermuda Triangle,South Pole,Loch Ness",
            "8 7,3,8",
            "9 South Korea,Russia,Germany",
            "10 London,Athens,Paris",
            "11 Eiffel Tower,Statue of Liberty,Big Ben,Sphinx,Red Square",
            "12 Monaco,Liechtenstein,San Marino,Andorra",
            "13 Texas,Connecticut,New Jersey",
            "14 Mexico City,New York,Beijing"
        ]

    choice = choices[question]
    only_choice = choice.split(f"{str(question)} ")[1]
    question_choices = only_choice.split(',')
    return question_choices

class load_select(discord.ui.Select):
    def __init__(self, question, questions, theme, correct):
        super().__init__()
        self.correct = correct
        self.question = question
        self.questions = questions
        self.theme = theme
        self.answer = load_answers(question, self.theme)
        choices = load_choices(question, self.theme)

        options = []
        responses = []

        if isinstance(self.answer, list):
            for ans in self.answer:
                responses.append(ans)
        else:
            responses.append(self.answer)

        for choice in choices:
            responses.append(choice)

        while responses:
            response = random.choice(responses)
            options.append(discord.SelectOption(label=response))
            responses.remove(response)

        self.options = options

    async def callback(self, interaction: discord.Interaction):
        if isinstance(self.answer, list):
            if any(value in self.answer for value in self.values):
                self.correct += 1
                increment_correct(interaction.user.id, self.theme)
        else:
            if self.values[0] == self.answer:
                self.correct += 1
                increment_correct(interaction.user.id, self.theme)

        await interaction.response.send_message("Answer recorded..")

        # Send the next question if available
        next_question_index = self.question + 1
        if next_question_index < len(self.questions):
            next_question = self.questions[next_question_index]
            em = discord.Embed(title=f"Question {next_question_index + 1}", description=next_question)
            await interaction.followup.send(embed=em, view=load_view(next_question_index, self.questions, self.theme, self.correct))
        else:
            await interaction.followup.send(f"You finished the quiz. You got {self.correct} answers correct!")

class load_view(discord.ui.View):
    def __init__(self, question_index, questions, theme, correct = 0):
        super().__init__(timeout=None)
        self.add_item(load_select(question_index, questions, theme, correct))