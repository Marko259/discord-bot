from datetime import datetime
from time import sleep

import discord
from helpers.config import GUILD_ID
from discord.ext import commands, tasks
from discord_slash import cog_ext
from helpers.message import embed
from helpers.database import db_connection
from helpers.youtube import Youtube

class MembersCog(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot

    guilds_id = [GUILD_ID]

    @cog_ext.cog_slash(name='vote2kick', guild_ids=guilds_id, description='Votes to kick a member')
    async def vote2kick(self, ctx, member: discord.Member, reason: str = False):
        """
        Command which votes to kick a member.
        """
        try:
            await ctx.send("Message is being generated", delete_after=5)
            mydb = db_connection()
            cursor = mydb.cursor()
            now = datetime.now()
            timestamp = now.strftime("%d/%m/%Y %H:%M:%S")
            footer = f"{ctx.author.display_name} has started a vote | {timestamp}"
            cursor.execute(f"SELECT * FROM vote2kick WHERE guild_id = {ctx.guild.id} AND member_user_id = {member.id}")
            if cursor.fetchone():
                await ctx.send(f"{member.mention} has already been voted to be kicked.")
                return
            async with ctx.channel.typing():
                sleep(2)
            msg = embed(description=reason, title=f"{member.display_name} has been voted to be kicked", User=member.id, author=ctx.author.display_name, avatar_url=ctx.author.avatar_url, footer=footer)
            message = await ctx.send(embed=msg)
            cursor.execute('INSERT into vote2kick (author_user_id, member_user_id, message_id, guild_id, reason, created_at) VALUES (%s, %s, %s, %s, %s, %s)', (ctx.author.id, member.id, message.id, ctx.guild.id, reason, now.strftime("%Y/%m/%d %H:%M:%S")))
            mydb.commit()
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')

def setup(bot):
    bot.add_cog(MembersCog(bot))