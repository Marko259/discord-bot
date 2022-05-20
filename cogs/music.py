import re
import aiohttp
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_choice, create_option
from helpers.queue import HZ_BANDS, TIME_REGEX, URL_REGEX, EQGainOutOfBounds, InvalidRepeatMode, InvalidTimeString, MaxVolume, MinVolume, NoLyricsFound, NoMoreTracks, NoPreviousTracks, NoVoiceChannel, NonExistentEQBand, PlayerIsAlreadyPaused, QueueIsEmpty, RepeatMode, AlreadyConnectedToChannel, VolumeTooHigh, VolumeTooLow
from helpers.player import Player
from helpers.config import GUILD_ID, LYRICS_URL
import wavelink
import discord
import datetime
import typing as t

class Music(commands.Cog, wavelink.WavelinkMixin):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.wavelink = wavelink.Client(bot=bot)
        self.bot.loop.create_task(self.start_nodes())

    guilds_id = [GUILD_ID]

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                await self.get_player(member.guild).teardown()

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node):
        print(f" Wavelink node `{node.identifier}` ready.")

    @wavelink.WavelinkMixin.listener('on_track_stuck')
    @wavelink.WavelinkMixin.listener("on_track_end")
    @wavelink.WavelinkMixin.listener("on_track_exception")
    async def on_player_stop(self, node, payload):
        if payload.player.queue.repeat_mode == RepeatMode.ONE:
            await payload.player.repeat_track()
        else:
            await payload.player.advance()
    
    async def cog_check(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("Music commands are not available in DMs.")
            return False
        return True
    
    async def start_nodes(self):
        await self.bot.wait_until_ready()

        nodes = {
            "MAIN": {
                "host": "127.0.0.1",
                "port": 2333,
                "rest_uri": "http://127.0.0.1:2333",
                "password": "youshallnotpass",
                "identifier": "MAIN",
                "region": "europe",
            }
        }

        for node in nodes.values():
            await self.wavelink.initiate_node(**node)

    def get_player(self, obj):
        if isinstance(obj, commands.Context):
            return self.wavelink.get_player(obj.guild.id, cls=Player, context=obj)
        elif isinstance(obj, discord.Guild):
            return self.wavelink.get_player(obj.id, cls=Player)
    
    @cog_ext.cog_slash(name="connect", guild_ids=guilds_id, description="Connect to a voice channel")
    async def connect_command(self, ctx, *, channel: t.Optional[discord.VoiceChannel]):
        player = self.get_player(ctx)
        channel = await player.connect(ctx, channel)
        await ctx.send(f"Connected to {channel.name}")

    @connect_command.error
    async def connect_command_error(self, ctx, error):
        if isinstance(error, AlreadyConnectedToChannel):
            await ctx.send("Already connected to a voice channel.")
        elif isinstance(error, NoVoiceChannel):
            await ctx.send("No suitable voice channel was provided.")

    @cog_ext.cog_slash(name="disconnect", guild_ids=guilds_id, description="Disconnect from a voice channel")
    async def disconnect_command(self, ctx):
        player = self.get_player(ctx)
        await player.teardown()
        await ctx.send("Disconnected from voice channel.")

    @cog_ext.cog_slash(name="play", guild_ids=guilds_id, description="Play a song")
    async def play_command(self, ctx, *, query: t.Optional[str]):
        player = self.get_player(ctx)
        
        if not player.is_connected:
            await player.connect(ctx)

        if query is None:
            if player.queue.is_empty:
                raise QueueIsEmpty

            await player.set_pause(False)
            await ctx.send("Resumed the music.")
        else:
            query = query.strip("<>")
            if not re.match(URL_REGEX, query):
                query = f"ytsearch:{query}"

            await player.add_tracks(ctx, await self.wavelink.get_tracks(query))
    
    @play_command.error
    async def play_command_error(self, ctx, error):
        if isinstance(error, QueueIsEmpty):
            await ctx.send("The queue is empty.")
        elif isinstance(error, NoVoiceChannel):
            await ctx.send("No voice channel was provided.")
    
    @cog_ext.cog_slash(name="pause", guild_ids=guilds_id, description="Pause the music")
    async def pause_command(self, ctx):
        player = self.get_player(ctx)
        if player.is_paused:
            raise PlayerIsAlreadyPaused

        await player.set_pause(True)
        await ctx.send("Paused the music.")

    @pause_command.error
    async def pause_command_error(self, ctx, error):
        if isinstance(error, PlayerIsAlreadyPaused):
            await ctx.send("The music is already paused.")

    @cog_ext.cog_slash(name="stop", guild_ids=guilds_id, description="Stop the music")
    async def stop_command(self, ctx):
        player = self.get_player(ctx)
        player.queue.empty()
        await player.stop()
        await ctx.send("Stopped the music.")

    @cog_ext.cog_slash(name="skip", guild_ids=guilds_id, description="Skip the current song")
    async def skip_command(self, ctx):
        player = self.get_player(ctx)

        if not player.queue.upcoming:
            raise NoMoreTracks

        await player.stop()
        await ctx.send("Skipped the current song.")
    
    @skip_command.error
    async def skip_command_error(self, ctx, error):
        if isinstance(error, QueueIsEmpty):
            await ctx.send("The queue is empty.")
        elif isinstance(error, NoMoreTracks):
            await ctx.send("There are no more songs in the queue.")
    
    @cog_ext.cog_slash(name="previous", guild_ids=guilds_id, description="Go back to the previous song")
    async def previous_command(self, ctx):
        player = self.get_player(ctx)

        if not player.queue.history:
            raise NoPreviousTracks

        player.queue.position -= 2
        await player.stop()
        await ctx.send("Going back to the previous song.")

    @previous_command.error
    async def previous_command_error(self, ctx, error):
        if isinstance(error, QueueIsEmpty):
            await ctx.send("The queue is empty.")
        elif isinstance(error, NoPreviousTracks):
            await ctx.send("There are no previous songs.")

    @cog_ext.cog_slash(name="shuffle", guild_ids=guilds_id, description="Shuffle the queue")
    async def shuffle_command(self, ctx):
        player = self.get_player(ctx)
        await player.queue.shuffle()
        await ctx.send("Shuffled the queue.")

    @shuffle_command.error
    async def shuffle_command_error(self, ctx, error):
        if isinstance(error, QueueIsEmpty):
            await ctx.send("The queue is empty.")
    
    @cog_ext.cog_slash(name="repeat", guild_ids=guilds_id, description="Repeat the current song")
    async def repeat_command(self, ctx, mode: str):
        if mode not in ("none", "1", "all"):
            raise InvalidRepeatMode
        
        player = self.get_player(ctx)
        player.queue.set_repeat_mode(mode)
        await ctx.send(f"Set the repeat mode to {mode}.")

    @cog_ext.cog_slash(name="queue", guild_ids=guilds_id, description="View the queue")
    async def queue_command(self, ctx, show: t.Optional[int] = 10):
        player = self.get_player(ctx)
        
        if player.queue.is_empty:
            raise QueueIsEmpty
        
        embed = discord.Embed(
            title="Queue",
            description=f"Showing up to next {show} tracks.",
            color=ctx.author.color,
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_author(name="Query Results")
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.add_field(
            name="Currently playing",
            value=getattr(player.queue.current_track, "title", "No tracks currently playing."),
            inline=False
        )
        if upcoming := player.queue.upcoming:
            embed.add_field(
                name="Next up",
                value="\n".join(t.title for t in upcoming[:show]),
                inline=False
            )

        msg = await ctx.send(embed=embed)
    
    @queue_command.error
    async def queue_command_error(self, ctx, error):
        if isinstance(error, QueueIsEmpty):
            await ctx.send("The queue is empty.")
    
    @cog_ext.cog_slash(name="volume", guild_ids=guilds_id, description="Change the volume",
    options=[
        create_option(
            name="type",
            description="The volume to set the player to.",
            option_type="3",
            required=False,
            choices=[
                create_choice(
                    name="Up",
                    value="up",
                ),
                create_choice(
                    name="Down",
                    value="down",
                )
            ]
        )
    ])
    async def volume_command(self, ctx, type: str = None, volume: int = None):
        player = self.get_player(ctx)
        if volume:
            if volume < 0:
                raise VolumeTooLow
            
            if volume > 150:
                raise VolumeTooHigh

            if type == "up":
                if player.volume == 150:
                    raise MaxVolume
                await player.set_volume(value := min(player.volume + 10, 150))
                await ctx.send(f"Volume set to {value:,}%")
            elif type == "down":
                if player.volume == 0:
                    raise MinVolume
                await player.set_volume(value := max(player.volume - 10, 0))
                await ctx.send(f"Volume set to {value:,}%")
    
    @volume_command.error
    async def volume_command_error(self, ctx, error):
        if isinstance(error, MaxVolume):
            await ctx.send("The volume is already at the maximum.")
        elif isinstance(error, MinVolume):
            await ctx.send("The volume is already at the minimum.")
    
    @cog_ext.cog_slash(name="lyrics", guild_ids=guilds_id, description="Get the lyrics of a song")
    async def lyrics_command(self, ctx, name: t.Optional[str]):
        player = self.get_player(ctx)
        name = name or player.queue.current_track.title
        
        async with ctx.typing():
            async with aiohttp.request("GET", LYRICS_URL + name, headers={}) as r:
                if not 200 <= r.status < 299:
                    raise NoLyricsFound
                
                data = await r.json()

                if len(data["lyrics"]) > 2000:
                    return await ctx.send(f"<{data['links']['genius']}>")
                
                embed = discord.Embed(
                    title=data["title"],
                    description=data["lyrics"],
                    color=ctx.author.color,
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_thumbnail(url=data["thumbnail"]["genius"])
                embed.set_author(name=data["author"])
                await ctx.send(embed=embed)

    @lyrics_command.error
    async def lyrics_command_error(self, ctx, error):
        if isinstance(error, NoLyricsFound):
            await ctx.send("No lyrics found.")
    
    @cog_ext.cog_slash(name="eq", guild_ids=guilds_id, description="Change the equalizer")
    async def eq_command(self, ctx, band: int, gain: float):
        player = self.get_player(ctx)

        if not 1 <= band <= 15 and band not in HZ_BANDS:
            raise NonExistentEQBand
        
        if band > 15:
            band = HZ_BANDS.index(band) + 1
        
        if abs(gain) > 10:
            raise EQGainOutOfBounds
        
        player.eq_levels[band - 1] = gain / 10
        eq = wavelink.eqs.Equalizer(levels=[(i, gain) for i, gain in enumerate(player.eq_levels)])
        await player.set_eq(eq)
        await ctx.send(f"Set the equalizer band {band} to {gain * 10:,}%.")
    
    @eq_command.error
    async def eq_command_error(self, ctx, error):
        if isinstance(error, NonExistentEQBand):
            await ctx.send(
                "This is a 15 band equaliser -- the band number should be between 1 and 15, or one of the following "
                "frequencies: " + ", ".join(str(b) for b in HZ_BANDS)
            )
        elif isinstance(error, EQGainOutOfBounds):
            await ctx.send("The EQ gain for any band should be between 10 dB and -10 dB.")

    @cog_ext.cog_slash(name="playing", guild_ids=guilds_id, description="View the currently playing track")
    async def playing_command(self, ctx):
        player = self.get_player(ctx)

        if not player.is_playing:
            raise PlayerIsAlreadyPaused
        
        embed = discord.Embed(
            title="Currently playing",
            colour=ctx.author.color,
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_author(name="Query Results")
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Currently playing", value=player.queue.current_track.title, inline=False)
        embed.add_field(name="Artist", value=player.queue.current_track.author, inline=False)
        
        position = divmod(player.position, 60000)
        length = divmod(player.queue.current_track.length, 60000)

        embed.add_field(
            name="Position",
            value=f"{int(position[0])}:{round(position[1]/1000):02}/{int(length[0])}:{round(length[1]/1000):02}",
            inline=False
        )
        await ctx.send(embed=embed)
    
    @playing_command.error
    async def playing_command_error(self, ctx, error):
        if isinstance(error, PlayerIsAlreadyPaused):
            await ctx.send("The player is already paused.")
        
    @cog_ext.cog_slash(name="skip_to", guild_ids=guilds_id, description="Skip to a specific time in the current track")
    async def skip_to_command(self, ctx, index: int):
        player = self.get_player(ctx)
        
        if player.queue.is_empty:
            raise QueueIsEmpty
        
        if not 0 <= index <= player.queue.length:
            raise NoMoreTracks
        
        player.queue.position = index - 2
        await player.stop()
        await ctx.send(f"Skipped to track {index}.")
    
    @skip_to_command.error
    async def skip_to_command_error(self, ctx, error):
        if isinstance(error, QueueIsEmpty):
            await ctx.send("The queue is empty.")
        elif isinstance(error, NoMoreTracks):
            await ctx.send("There are no more tracks.")
    
    @cog_ext.cog_slash(name="restart", guild_ids=guilds_id, description="Restart the current track")
    async def restart_command(self, ctx):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty
        
        await player.seek(0)
        await ctx.send("Restarted the current track.")
    
    @restart_command.error
    async def restart_command_error(self, ctx, error):
        if isinstance(error, QueueIsEmpty):
            await ctx.send("The queue is empty.")
    
    @cog_ext.cog_slash(name="seek", guild_ids=guilds_id, description="Seek to a specific time in the current track")
    async def seek_command(self, ctx, position: str):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty
        
        if not (match := re.match(TIME_REGEX, position)):
            raise InvalidTimeString
        
        if match.group(3):
            secs = (int(match.group(1) * 60) + (int(match.group(3))))
        else:
            secs = int(match.group(1))
        
        await player.seek(secs * 1000)
        await ctx.send(f"Seeked to {position}.")
    
    def setup(bot):
        bot.add_cog(Music(bot))