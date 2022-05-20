import discord
import youtube_dl
from helpers.config import GUILD_ID
from discord.ext import commands, tasks
from discord_slash import cog_ext
from helpers.youtube import Youtube

class PlayCog(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot

    guilds_id = [GUILD_ID]
    queue = {}

    def addToQueue(self, guild, song):
        if guild.id in self.queue:
            self.queue[guild.id] = []
        elif guild.id not in self.queue:
            self.queue.update({guild.id: []})
        self.queue[guild.id].append(song)


    async def playSong(self, ctx, channel):
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
        async with ctx.channel.typing():
            song = self.queue[ctx.guild.id].pop(0)
            if song == None:
                return
            player = await Youtube.from_url(song, loop=self.bot.loop, stream=True, ytdl=ytdl)
            channel.play(player, after=lambda e: print('Player error: %s' % e) if e else self.playSong(ctx, channel))

    @cog_ext.cog_slash(name="test3", guild_ids=guilds_id, description="Test")
    async def test3(self, ctx, *, member: discord.Member):
        """
        Test command
        """
        try:
            await ctx.send(f"{member.mention}")
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')

    @cog_ext.cog_slash(name='play', guild_ids=guilds_id, description='Play a song')
    async def play(self, ctx, *, song: str):
        """
        Command which plays a song.
        """
        if not ctx.author.voice:
            await ctx.send("You are not in a voice channel")
            return
        else:
            channel = ctx.author.voice.channel
        
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if channel != voice and voice is None:
            voice = await channel.connect()
        elif channel != voice and voice is not None:
            await ctx.send("Bot already connected to a channel")
            return
        
        server = ctx.guild
        vc = server.voice_client
        self.addToQueue(server, song)
        await self.playSong(ctx, vc)
        # channel = ctx.author.voice.channel
        # if not channel:
        #     await ctx.send('You are not in a voice channel.')
        #     return

        # youtube_dl.utils.bug_reports_message = lambda: ''
        
        # ytdl_format_options = {
        #     'format': 'bestaudio/best',
        #     'restrictfilenames': True,
        #     'noplaylist': True,
        #     'nocheckcertificate': True,
        #     'ignoreerrors': False,
        #     'logtostderr': False,
        #     'quiet': True,
        #     'no_warnings': True,
        #     'default_search': 'auto',
        #     'source_address': '0.0.0.0'
        # }

        # ffmpeg_options = {
        #     'options': '-vn'
        # }

        # ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
        # try:
        #     filename = await Youtube.from_url(song, loop=self.bot.loop, ytdl=ytdl)
        #     if not ctx.guild.voice_client in self.bot.voice_clients:
        #         await channel.connect()
            
        #     server = ctx.guild
        #     voice_channel = server.voice_client
        #     voice_channel.play(discord.FFmpegPCMAudio(source=filename))

        #     await ctx.send(f'**Now playing:** {song}')
        # except Exception as e:
        #     await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')

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

def setup(bot):
    bot.add_cog(PlayCog(bot))