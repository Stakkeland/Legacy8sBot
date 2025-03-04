import discord
from discord.ext import commands
import random
import asyncio
from database import conn, cursor
from match_manager import MatchManager
from maps import queues, hardpoints, snds, dominations, ctfs

class QueueView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.queues = queues
        self.create_buttons()
        self.match_manager = MatchManager(self)

    def create_buttons(self):
        for game in self.queues.keys():
            join_button = self.create_join_button(game)
            self.add_item(join_button)
        leave_button = self.create_leave_button()
        self.add_item(leave_button)

    def create_join_button(self, game):
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