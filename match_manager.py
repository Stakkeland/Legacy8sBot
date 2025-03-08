import discord
import random
import asyncio
from collections import Counter
from database import conn, cursor
from voting import VotingManager, Voting
from maps import hardpoints, snds, dominations, ctfs

class MatchManager:
    def __init__(self, queue_view):
        self.queue_view = queue_view
        self.voting_manager = VotingManager(self)
        self.voting = Voting()
        self.create_teams_lock = asyncio.Lock()
        self.team1 = []
        self.team2 = []
        self.category = None

    def create_mapset(self, game):
        if game in ["MWIII 2023", "MWII 2022", "Vanguard", "Cold War", "MW 2019", "Black Ops 4", "World War II", "Infinite Warfare", "Black Ops 3", "Advanced Warfare", "Black Ops 2"]:
            hardpoint1 = random.choice(hardpoints[game])
            hardpoint2 = random.choice(hardpoints[game])
            while hardpoint1 == hardpoint2:
                hardpoint2 = random.choice(hardpoints[game])
            snd = random.choice(snds[game])
            embed = discord.Embed(title="Mapset", color=discord.Color.blue())
            embed.add_field(name="Hardpoint:", value=hardpoint1, inline=True)
            embed.add_field(name="Hardpoint:", value=hardpoint2, inline=True)
            embed.add_field(name="SND:", value=snd, inline=True)
        elif game in ["Modern Warfare 3", "Black Ops 1", "Modern Warfare 2"]:
            snd1 = random.choice(snds[game])
            snd2 = random.choice(snds[game])
            while snd1 == snd2:
                snd2 = random.choice(snds[game])
            ctf = random.choice(ctfs[game])
            embed = discord.Embed(title="Mapset", color=discord.Color.blue())
            embed.add_field(name="SND:", value=snd1, inline=True)
            embed.add_field(name="SND:", value=snd2, inline=True)
            embed.add_field(name="Capture the Flag:", value=ctf, inline=True)
        elif game in ["World at War", "COD4", "Ghosts","COD4 Remastered"]:
            snd1 = random.choice(snds[game])
            snd2 = random.choice(snds[game])
            while snd1 == snd2:
                snd2 = random.choice(snds[game])
            dom = random.choice(dominations[game])
            embed = discord.Embed(title="Mapset", color=discord.Color.blue())
            embed.add_field(name="SND:", value=snd1, inline=True)
            embed.add_field(name="SND:", value=snd2, inline=True)
            embed.add_field(name="Domination:", value=dom, inline=True)
        return embed

    async def create_account(self, interaction: discord.Interaction, user: discord.User):
        cursor.execute('SELECT * FROM users WHERE id = ?', (user.id,))
        account = cursor.fetchone()
        if account is None:
            cursor.execute('''
            INSERT INTO users (id, name, mp, mp_wins, mp_losses, sr, rank, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user.id, user.name, 0, 0, 0, 600, "Bronze", "unknown"))
            conn.commit()

    async def create_teams_embed(self, interaction, team1, team2):
        embed = discord.Embed(title="Players", color=discord.Color.green())
        embed.add_field(name="Team 1", value=" ", inline=False)
        for i, member in enumerate(team1):
            await self.create_account(interaction, member)
            cursor.execute('SELECT location FROM users WHERE id = ?', (member.id,))
            location = cursor.fetchone()[0]
            embed.add_field(name=i+1, value=f"{member.mention}   -   {location}", inline=False)
        embed.add_field(name="Team 2", value=" ", inline=False)
        for i, member in enumerate(team2):
            await self.create_account(interaction, member)
            cursor.execute('SELECT location FROM users WHERE id = ?', (member.id,))
            location = cursor.fetchone()[0]
            embed.add_field(name=i+1, value=f"{member.mention}   -   {location}", inline=False)
        embed.add_field(name="\u200b", value="\u200b", inline=False)

        locations = [cursor.execute('SELECT location FROM users WHERE id = ?', (member.id,)).fetchone()[0] for member in team1 + team2]
        location_counts = Counter(locations)
        most_common_locations = location_counts.most_common()

        if len(most_common_locations) > 1 and most_common_locations[0][1] == most_common_locations[1][1]:
            tied_locations = [loc for loc, count in most_common_locations if count == most_common_locations[0][1]]
            embed.add_field(name="Recommended Host Locations:", value=", ".join(tied_locations), inline=False)
        else:
            most_common_location = most_common_locations[0][0]
            embed.add_field(name="Recommended Host Location:", value=most_common_location, inline=False)

        return embed

    async def create_teams(self, interaction, channel, queue, game):
        async with self.create_teams_lock:
            if hasattr(self, 'category') and self.category is not None:
                return

        random.shuffle(queue)
        half_size = len(queue) // 2
        self.team1 = queue[:half_size]
        self.team2 = queue[half_size:]

        guild = channel.guild
        self.category = await guild.create_category(f"{game} Match")
        match_channel = await self.category.create_text_channel(f"{game} Match Chat")
        team1_channel = await self.category.create_voice_channel("Team 1")
        team2_channel = await self.category.create_voice_channel("Team 2")

        team1_invite = await team1_channel.create_invite(max_age=300)
        team2_invite = await team2_channel.create_invite(max_age=300)

        mapset_embed = self.create_mapset(game)
        await match_channel.send(f"Welcome to your {game} match!", silent=True)
        await match_channel.send(embed=mapset_embed, silent=True)

        teams_embed = await self.create_teams_embed(interaction, self.team1, self.team2)
        await match_channel.send(embed=teams_embed, silent=True)

        for member in self.team1:
            try:
                await member.send(f"You have been assigned to Team 1 for {game}. Join the voice channel using this link: {team1_invite}")
            except discord.Forbidden:
                await channel.send(f"Could not send invite to {member.name}.", ephemeral=True)
        
        for member in self.team2:
            try:
                await member.send(f"You have been assigned to Team 2 for {game}. Join the voice channel using this link: {team2_invite}")
            except discord.Forbidden:
                await channel.send(f"Could not send invite to {member.name}.", ephemeral=True)

        queue.clear()

        countdown_message = await match_channel.send("Channels and Match will end if all users do not join in the next 4 minutes", silent=True)
        await self.schedule_initial_check(self.category, 1, self.team1 + self.team2, countdown_message, match_channel)

    async def schedule_initial_check(self, category, delay_mins, members, countdown_message, match_channel):
        voting = Voting()
        for i in range(delay_mins, 0, -1):
            for j in range(60, 0, -1):
                if self.all_members_in_voice_channels(category, members):
                    await countdown_message.delete()
                    await self.voting_manager.send_voting_buttons(match_channel, voting)
                    await self.schedule_extended_check(category, members)
                    return
                else:
                    await countdown_message.edit(content=f"Channels and Match will end if all users do not join in the next {i+1} minutes")
                    await asyncio.sleep(1)
    
        for i in range(60, 0, -1):
            if self.all_members_in_voice_channels(category, members):
                await countdown_message.delete()
                await self.voting_manager.send_voting_buttons(match_channel, voting)
                await self.schedule_extended_check(category, members)
                return
            else:
                await countdown_message.edit(content=f"Channels and Match will end if all users do not join in the next {i} seconds")
                await asyncio.sleep(1)
    
        await self.delete_category_and_channels(category)

    async def schedule_extended_check(self, category, members):
        for _ in range(35):
            if category not in category.guild.categories:
                return
            await asyncio.sleep(60)

        while True:
            if category not in category.guild.categories:
                return
            if not self.all_members_in_voice_channels(category, members):
                await self.delete_category_and_channels(category)
                return
            await asyncio.sleep(5 * 60)
 
    def all_members_in_voice_channels(self, category, members):
        return all(any(member in vc.members for vc in category.voice_channels) for member in members)

    async def delete_category_and_channels(self, category):
        try:
            for channel in category.channels:
                try:
                    await channel.delete()
                except discord.NotFound:
                    print(f"Channel {channel.name} not found. It may have already been deleted.")
            await category.delete()
        except discord.NotFound:
            print(f"Category {category.name} not found. It may have already been deleted.")
        finally:
            self.category = None
            self.team1 = []
            self.team2 = []