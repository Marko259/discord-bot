import os
import datetime

from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from helpers.tools import staff_roles
from helpers.config import COGS_LOAD, GUILD_ID, DEBUG

class AdminCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    guilds_id = [GUILD_ID]

    @cog_ext.cog_slash(name='load', guild_ids=guilds_id, description='Loads a cogs')
    @commands.has_any_role(*staff_roles())
    async def load(self, ctx, *, cog: str):
        """
        Command which Loads a Module.
        """
        try:
            if cog == 'All':
                for cogs in COGS_LOAD:
                    self.bot.load_extension(COGS_LOAD[cogs])
            else:
                self.bot.load_extension(COGS_LOAD[cog])
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send(f'**`SUCCESS`**')

    @cog_ext.cog_slash(name='unload', guild_ids=guilds_id, description='Unloads a cogs')
    @commands.has_any_role(*staff_roles())
    async def unload(self, ctx, *, cog: str):
        """
        Command which Unloads a Module.
        """
        try:
            if cog == 'All':
                for cogs in COGS_LOAD:
                    self.bot.unload_extension(COGS_LOAD[cogs])
            else:
                self.bot.unload_extension(COGS_LOAD[cog])
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send(f'**`SUCCESS`**')

    @cog_ext.cog_slash(name='reload', guild_ids=guilds_id, description='Reloads a cogs')
    @commands.has_any_role(*staff_roles())
    async def reload(self, ctx, *, cog: str):
        """
        Command which Reloads a Module.
        """
        try:
            if cog == 'All':
                for cogs in COGS_LOAD:
                    self.bot.reload_extension(COGS_LOAD[cogs])
            else:
                self.bot.reload_extension(COGS_LOAD[cog])
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send(f'**`SUCCESS`**')

    @cog_ext.cog_slash(name="ping", guild_ids=guilds_id, description='Pong!')
    @commands.has_any_role(*staff_roles())
    async def ping(self, ctx):
        """
        Command which pings the bot.
        """
        await ctx.reply(f'**`Pong!`**')

    @cog_ext.cog_slash(name="delete", guild_ids=guilds_id, description='Function deletes specific amount of messages.')
    @commands.has_any_role(*staff_roles())
    async def delete(self, ctx, amount: int = 0):
        """
        Function deletes specific amount of messages
        :param ctx:
        :param number:
        :return None:
        :raise Exception:
        """
        if DEBUG == True:
            try:
                msg_delete = []
                async for msg in ctx.channel.history(limit=amount):
                    msg_delete.append(msg)

                msgs = await ctx.send("Deleting messages")
                await msgs.channel.purge(limit=amount)
            except Exception as exception:
                await ctx.send(exception)
        else:
            await ctx.author.send('Command is disabled because debug is not enabled.')

def setup(bot):
    bot.add_cog(AdminCog(bot))
    
