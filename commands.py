from discord.ext import commands
from database import conn, cursor
import discord

def setup_commands(bot):
    @bot.command(name='create_account')
    async def create_account(ctx, location):
        valid_locations = ['west', 'central', 'east', 'eu', 'china', 'australia', 'south america', 'africa', 'unknown']
        if location.lower() not in valid_locations:
            await ctx.send(f"Invalid location. Please choose from: {', '.join(valid_locations)}")
            return
        cursor.execute('SELECT * FROM users WHERE id = ?', (ctx.author.id,))
        user = cursor.fetchone()
        if user is not None:
            await ctx.send(f"You already have an account, {ctx.author.name}!")
        else:
            cursor.execute('''
            INSERT INTO users (id, name, mp, mp_wins, mp_losses, sr, rank, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (ctx.author.id, ctx.author.name, 0, 0, 0, 600, "Bronze", location))
            conn.commit()
            await ctx.send(f"Account created for {ctx.author.name} with location {location}")

    @bot.command(name='change_location')
    async def change_location(ctx, new_location):
        valid_locations = ['west', 'central', 'east', 'eu', 'china', 'australia', 'south america', 'africa', 'unknown']
        if new_location.lower() not in valid_locations:
            await ctx.send(f"Invalid location. Please choose from: {', '.join(valid_locations)}")
            return
        cursor.execute('SELECT * FROM users WHERE id = ?', (ctx.author.id,))
        user = cursor.fetchone()
        if user is None:
            await ctx.send(f"You do not have an account yet, {ctx.author.name}. Please create one first using !create_account.")
        else:
            cursor.execute('UPDATE users SET location = ? WHERE id = ?', (new_location, ctx.author.id))
            conn.commit()
            await ctx.send(f"Location updated to {new_location} for {ctx.author.name}")

    @bot.command(name='view_stats')
    async def view_stats(ctx):
        cursor.execute('SELECT name, sr, rank, mp, mp_wins, mp_losses FROM users WHERE id = ?', (ctx.author.id,))
        user = cursor.fetchone()
        if user is None:
            await ctx.send(f"You do not have an account yet, {ctx.author.name}. Please create one first using !create_account.")
        else:
            name, sr, rank, mp, mp_wins, mp_losses = user
            embed = discord.Embed(title=f"{name}'s Stats", color=discord.Color.blue())
            embed.add_field(name="Skill Rating (SR)", value=sr, inline=True)
            embed.add_field(name="Rank", value=rank, inline=True)
            embed.add_field(name="Matches Played", value=mp, inline=True)
            embed.add_field(name="Matches Won", value=mp_wins, inline=True)
            embed.add_field(name="Matches Lost", value=mp_losses, inline=True)
            if ctx.author.avatar:
                embed.set_thumbnail(url=ctx.author.avatar.url)
            await ctx.send(embed=embed)