from discord.ext import commands
from database import conn, cursor
import discord

def setup_commands(bot):
    @bot.command(name='create_account')
    async def create_account(ctx, location):
        '''Create an account for the user'''
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
        '''Change the location of the users account'''
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
        '''Sends an embed message showing most important stats of the user'''
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
            
            # Add logo based on rank
            rank_logo_map = {
                "Bronze": "logobronze.jpg",
                "Silver": "logosilver.jpg",
                "Gold": "logogold.jpg",
                "Platinum": "logoplatinum.jpg",
                "Diamond": "logodiamond.jpg",
                "Master": "logomaster.jpg",
                "Grandmaster": "logograndmaster.jpg",
                "Overlord" : "logooverlord.jpg"
            }
            logo_filename = rank_logo_map.get(rank, "logobronze.jpg")
            logo_path = f"c:/Legacy8sBot/logopictures/{logo_filename}"
            file = discord.File(logo_path, filename=logo_filename)
            embed.set_thumbnail(url=f"attachment://{logo_filename}")
            
            await ctx.send(file=file, embed=embed)