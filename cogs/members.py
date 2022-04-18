import youtube_dl

import discord
from helpers.config import GUILD_ID
from discord.ext import commands, tasks
from discord_slash import cog_ext
from helpers.youtube import Youtube

class MembersCog(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot

    guilds_id = [GUILD_ID]

    @cog_ext.cog_slash(name='play', guild_ids=guilds_id, description='Play a song')
    async def play(self, ctx, *, song: str):
        """
        Command which plays a song.
        """
        channel = ctx.author.voice.channel
        if not channel:
            await ctx.send('You are not in a voice channel.')
            return

        youtube_dl.utils.bug_reports_message = lambda: ''
        
        ytdl_format_options = {
            'format': 'bestaudio/best',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0'
        }

        ffmpeg_options = {
            'options': '-vn'
        }

        ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
        try:
            filename = await Youtube.from_url(song, loop=self.bot.loop, ytdl=ytdl)
            if not ctx.guild.voice_client in self.bot.voice_clients:
                await channel.connect()
            
            server = ctx.guild
            voice_channel = server.voice_client
            voice_channel.play(discord.FFmpegPCMAudio(source=filename))

            await ctx.send(f'**Now playing:** {song}')
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')

    @cog_ext.cog_slash(name='stop', guild_ids=guilds_id, description='Stops the music')
    async def stop(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client.is_playing():
            await voice_client.stop()
            await ctx.send('**Stopped music**')
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    @cog_ext.cog_slash(name='pause', guild_ids=guilds_id, description='Pauses the music')
    async def pause(self, ctx):
        """
        Command which pauses the music.
        """
        voice_client = ctx.guild.voice_client
        if voice_client.is_playing():
            voice_client.pause()
            await ctx.send('Music has now been **Paused**')
        else:
            await ctx.send("The bot is not playing anything at the moment.")
    
    @cog_ext.cog_slash(name='resume', guild_ids=guilds_id, description='Resumes the music')
    async def resume(self, ctx):
        """
        Command which resumes the music.
        """
        voice_client = ctx.guild.voice_client
        if voice_client.is_paused():
            voice_client.resume()
            await ctx.send('Music has now been **Resumed**')
        else:
            await ctx.send("The bot is not paused at the moment.")

    @cog_ext.cog_slash(name='leave', guild_ids=guilds_id, description='Leaves the voice channel')
    async def leave(self, ctx):
        """
        Command which leaves the voice channel.
        """
        voice_client = ctx.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()

    @cog_ext.cog_slash(name='vote2kick', guild_ids=guilds_id, description='Votes to kick a member')
    async def vote2kick(self, ctx, member: discord.Member):
        """
        Command which votes to kick a member.
        """
        if member.id == ctx.author.id:
            await ctx.send('You cannot vote to kick yourself.')
            return
        if member.id == self.bot.user.id:
            await ctx.send('You cannot vote to kick me.')
            return
        if member.id in self.bot.config.get('voted_to_kick'):
            await ctx.send(f'You have already voted to kick {member.mention}.')
            return
        self.bot.config.set('voted_to_kick', member.id)
        await ctx.send(f'You have voted to kick {member.mention}.')

        if len(self.bot.config.get('voted_to_kick')) >= 3:
            await ctx.send('**Vote to kick has ended.**')
            self.bot.config.set('voted_to_kick', [])
            await member.move_to()

def setup(bot):
    bot.add_cog(MembersCog(bot))