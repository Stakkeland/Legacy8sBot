import discord
from discord.ext import commands
from queue_manager import QueueView
from database import conn, cursor
from commands import setup_commands
import asyncio

BOT_TOKEN = ""
CHANNEL_ID = 1333649194639949825

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    try:
        channel = bot.get_channel(CHANNEL_ID)
        if channel is None:
            print(f"Channel with ID {CHANNEL_ID} not found.")
            return

        embed = discord.Embed(
            description="Join a queue by clicking it's button below.",
            title="Queue Manager"
        )
        embed.set_footer(text="CDL Legacy 8's")

        view = QueueView()
        embed_message = None

        async def update_embed():
            nonlocal embed_message
            if embed_message is None:
                embed_message = await channel.send(embed=embed, view=view)
            while True:
                try:
                    embed.clear_fields()
                    for i, (game, queue) in enumerate(view.queues.items()):
                        embed.add_field(name=f"{game}   ", value=f": {len(queue)}", inline=True)
                    embed.color = discord.Color.green()
                    await embed_message.edit(embed=embed)
                except discord.NotFound:
                    print("Embed message not found. Recreating embed message.")
                    embed_message = await channel.send(embed=embed, view=view)
                except discord.HTTPException as e:
                    print(f"HTTPException occurred: {e}")
                await asyncio.sleep(1)

        bot.loop.create_task(update_embed())
    except Exception as e:
        print(f"Exception in on_ready: {e}")

def main():
    setup_commands(bot)
    bot.run(BOT_TOKEN)

if __name__ == "__main__":
    main()