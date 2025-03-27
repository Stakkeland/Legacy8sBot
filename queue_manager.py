import discord
from discord.ext import commands
import random
import asyncio
from database import conn, cursor
from match_manager import MatchManager
from maps import queues, hardpoints, snds, dominations, ctfs

class QueueView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.queues = queues
        self.create_buttons()
        self.match_manager = MatchManager(self)

    def create_buttons(self):
        '''displays all buttons on the homescreen, Call of duty titles, leave, and status'''
        for game in self.queues.keys():
            join_button = self.create_join_button(game)
            self.add_item(join_button)
        leave_button = self.create_leave_button()
        status_button = self.create_status_button()
        self.add_item(leave_button)
        self.add_item(status_button)

    def create_join_button(self, game):
        '''Creates buttons on homescreen for Call of Duty titles and checks if amount is met'''
        button = discord.ui.Button(label=game, style=discord.ButtonStyle.success)

        async def join_queue(interaction: discord.Interaction):
            user = interaction.user
            for other_game, queue in self.queues.items():
                if user in queue:
                    await interaction.response.send_message(f"You are already in the {other_game} queue!", ephemeral=True)
                    await asyncio.sleep(6)
                    await interaction.delete_original_response()
                    return

            queue = self.queues[game]
            queue.append(user)

            await interaction.response.send_message(f"You joined the {game} queue!", ephemeral=True)
            await asyncio.sleep(6)
            await interaction.delete_original_response()
            
            if game in ["MW 2019", "Black Ops 4"]:
                if len(queue) == 10:
                    await self.match_manager.create_teams(interaction, interaction.channel, queue, game)
            else:
                if len(queue) == 2:  # should be 8
                    await self.match_manager.create_teams(interaction, interaction.channel, queue, game)

        button.callback = join_queue
        return button

    def create_leave_button(self):
        '''Creates the leave button that enables a user to leave there queue'''
        button = discord.ui.Button(label="Leave Queue", style=discord.ButtonStyle.danger)

        async def leave_queue(interaction: discord.Interaction):
            user = interaction.user
            for game, queue in self.queues.items():
                if user in queue:
                    queue.remove(user)
                    await interaction.response.send_message(f"You left the {game} queue", ephemeral=True)
                    await asyncio.sleep(6)
                    await interaction.delete_original_response()
                    return
            await interaction.response.send_message(f"You are not in any queue.", ephemeral=True)
            await asyncio.sleep(6)
            await interaction.delete_original_response()

        button.callback = leave_queue
        return button

    def create_status_button(self):
        '''Creates the status button that enables a user to see where they reside in the queues'''
        button = discord.ui.Button(label="Status", style=discord.ButtonStyle.secondary)

        async def check_status(interaction: discord.Interaction):
            user = interaction.user
            for game, queue in self.queues.items():
                if user in queue:
                    await interaction.response.send_message(f"You are in the {game} queue.", ephemeral=True)
                    await asyncio.sleep(6)
                    await interaction.delete_original_response()
                    return
            await interaction.response.send_message(f"You are not in any queue.", ephemeral=True)
            await asyncio.sleep(6)
            await interaction.delete_original_response()

        button.callback = check_status
        return button