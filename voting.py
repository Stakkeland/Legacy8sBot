import discord
import asyncio
from database import conn, cursor

class Voting:
    def __init__(self):
        self.team1_votes = 0
        self.team2_votes = 0
        self.cancel_votes = 0
        self.voters = {}

    def get_team1_votes(self):
        return self.team1_votes

    def get_team2_votes(self):
        return self.team2_votes

    def get_cancel_votes(self):
        return self.cancel_votes

class VotingManager:
    def __init__(self, match_manager):
        self.match_manager = match_manager

    async def send_voting_buttons(self, match_channel, voting):
        '''Once all people have joined the lobby this sends the team voting buttons and embed'''
        embed = discord.Embed(
            title="Which team won?",
            description="Vote for the winning team below",
            color=discord.Color.gold()
        )
        embed.add_field(name="Team 1", value=f" Votes: {voting.get_team1_votes()}", inline=True)
        embed.add_field(name="Team 2", value=f" Votes: {voting.get_team2_votes()}", inline=True)
        embed.add_field(name="Cancel The Match", value=f" Votes: {voting.get_cancel_votes()}", inline=True)
        view = discord.ui.View()
        self.create_voting_buttons(view, voting)
        await match_channel.send(embed=embed, view=view)

    def create_voting_buttons(self, view, voting):
        '''Creates buttons to be used in send voting buttons'''
        team1_button = discord.ui.Button(label="Team 1", style=discord.ButtonStyle.primary)
        team2_button = discord.ui.Button(label="Team 2", style=discord.ButtonStyle.primary)
        cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger)

        team1_button.callback = lambda interaction: self.vote_team1(interaction, voting)
        team2_button.callback = lambda interaction: self.vote_team2(interaction, voting)
        cancel_button.callback = lambda interaction: self.cancel_match(interaction, voting)

        view.add_item(team1_button)
        view.add_item(team2_button)
        view.add_item(cancel_button)

    async def vote_team1(self, interaction: discord.Interaction, voting):
        '''Allows user to vote for team 1 and keep track of vote'''
        user = interaction.user
        await interaction.response.defer()
        if user.id in voting.voters:
            await self.change_vote(interaction, voting, user.id, "team1")
        else:
            voting.team1_votes += 1
            voting.voters[user.id] = "team1"
            await self.update_voting_embed(interaction, voting)
            await self.check_votes(interaction, voting)

    async def vote_team2(self, interaction: discord.Interaction, voting):
        '''Allows user to vote for team 2 and keep track of vote'''
        user = interaction.user
        await interaction.response.defer()
        if user.id in voting.voters:
            await self.change_vote(interaction, voting, user.id, "team2")
        else:
            voting.team2_votes += 1
            voting.voters[user.id] = "team2"
            await self.update_voting_embed(interaction, voting)
            await self.check_votes(interaction, voting)

    async def cancel_match(self, interaction: discord.Interaction, voting):
        '''Allows user to vote to cancel that match and keep track of vote'''
        user = interaction.user
        await interaction.response.defer()
        if user.id in voting.voters:
            await self.change_vote(interaction, voting, user.id, "cancel")
        else:
            voting.cancel_votes += 1
            voting.voters[user.id] = "cancel"
            await self.update_voting_embed(interaction, voting)
            await self.check_votes(interaction, voting)

    async def change_vote(self, interaction: discord.Interaction, voting, user_id, new_vote):
        '''Allows users to change vote easily and seamlessly'''
        previous_vote = voting.voters.get(user_id)
        if previous_vote == "team1":
            voting.team1_votes -= 1
        elif previous_vote == "team2":
            voting.team2_votes -= 1
        elif previous_vote == "cancel":
            voting.cancel_votes -= 1

        if new_vote == "team1":
            voting.team1_votes += 1
        elif new_vote == "team2":
            voting.team2_votes += 1
        elif new_vote == "cancel":
            voting.cancel_votes += 1

        voting.voters[user_id] = new_vote
        await self.update_voting_embed(interaction, voting)
        await self.check_votes(interaction, voting)

    async def update_voting_embed(self, interaction: discord.Interaction, voting):
        '''Ensures the votes on the voting embed are displayed to the correct amount'''
        embed = discord.Embed(
            title="Which team won?",
            description="Vote for the winning team below",
            color=discord.Color.gold()
        )
        embed.add_field(name="Team 1", value=f" Votes: {voting.get_team1_votes()}", inline=True)
        embed.add_field(name="Team 2", value=f" Votes: {voting.get_team2_votes()}", inline=True)
        embed.add_field(name="Cancel The Match", value=f" Votes: {voting.get_cancel_votes()}", inline=True)
        try:
            await interaction.message.edit(embed=embed)
        except discord.NotFound:
            print("Channel or message not found. It may have been deleted.")

    async def check_votes(self, interaction: discord.Interaction, voting):
        '''Checks the votes by the users, once 1 reaches the threshold it finalizes the match or cancels'''
        #game = self.category.name.split()[0]  # Extract the game name from the category name
        #required_votes = 6 if game in ["MW 2019", "Black Ops 4"] else 5
        required_votes = 2  # testing value
        if voting.team1_votes >= required_votes:
            await self.finalize_match(interaction, "Team 1")
        elif voting.team2_votes >= required_votes:
            await self.finalize_match(interaction, "Team 2")
        elif voting.cancel_votes >= required_votes:
            if interaction.channel:
                message = await interaction.channel.send("The match has been cancelled.")
            await asyncio.sleep(5)
            await message.delete()
            await self.match_manager.delete_category_and_channels(self.match_manager.category)
            async with self.match_manager.create_teams_lock:
                self.match_manager.category = None
                self.match_manager.team1 = []
                self.match_manager.team2 = []
            pass ## could be the issue I experienced with Payten

    async def update_rank(self, member_id):
        '''Updates users rank if threshold sr is met'''
        cursor.execute('''
        UPDATE users
        SET rank = CASE
            WHEN sr BETWEEN 0 AND 1200 THEN 'Bronze'
            WHEN sr BETWEEN 1201 AND 1800 THEN 'Silver'
            WHEN sr BETWEEN 1801 AND 2400 THEN 'Gold'
            WHEN sr BETWEEN 2401 AND 3000 THEN 'Platinum'
            WHEN sr BETWEEN 3001 AND 3600 THEN 'Diamond'
            WHEN sr BETWEEN 3601 AND 4200 THEN 'Master'
            WHEN sr BETWEEN 4201 AND 4800 THEN 'Iridescent'
            WHEN sr > 4801 THEN 'Grandmaster'
            ELSE rank
        END
        WHERE id = ?;
        ''', (member_id,))
        conn.commit()

    async def finalize_match(self, interaction: discord.Interaction, winning_team):
        '''Ends the match by updating all users stats and deleting all created channels and category'''
        await interaction.channel.send(f"{winning_team} has won the match!")
        for member in self.match_manager.team1 + self.match_manager.team2:
            cursor.execute('UPDATE users SET mp = mp + 1 WHERE id = ?', (member.id,))
            if member in (self.match_manager.team1 if winning_team == "Team 1" else self.match_manager.team2):
                cursor.execute('UPDATE users SET sr = sr + 24, mp_wins = mp_wins + 1 WHERE id = ?', (member.id,))
            else:
                cursor.execute('UPDATE users SET sr = sr - 11, mp_losses = mp_losses + 1 WHERE id = ?', (member.id,))
            await self.update_rank(member.id)
        conn.commit()
        
        # Cancel the schedule_extended_check loop
        self.match_manager.cancel_extended_check = True
        
        await asyncio.sleep(5)
        await self.match_manager.delete_category_and_channels(self.match_manager.category)
        async with self.match_manager.create_teams_lock:
            self.match_manager.category = None
            self.match_manager.team1 = []
            self.match_manager.team2 = []