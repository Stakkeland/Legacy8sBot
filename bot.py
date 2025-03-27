import discord
from discord.ext import commands
from queue_manager import QueueView
from database import conn, cursor
from commands import setup_commands
import asyncio

BOT_TOKEN = ""

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

active_channels = set()

@bot.command(name="start")
async def start(ctx):
    try:
        channel = ctx.channel

        if channel.id in active_channels:
            await ctx.send("A queue manager is already active in this channel.")
            return

        active_channels.add(channel.id)

        embed = discord.Embed(
            description="Join a queue by clicking its button below.",
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
        print(f"Exception in start command: {e}")

def main():
    setup_commands(bot)
    bot.run(BOT_TOKEN)

if __name__ == "__main__":
    main()