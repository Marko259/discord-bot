import discord
from discord import InvalidArgument
from discord_slash import SlashCommand
from discord.ext import commands
from dotenv import load_dotenv
from helpers import config
from helpers.config import BOT_TOKEN

load_dotenv('.env')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', description=config.DESCRIPTION, intents=intents, help_command=None, case_insensitive=True)
slash = SlashCommand(bot, sync_commands=True)

"""
    Bot event that sets bots rich presence in Discord profile
"""
@bot.event
async def on_ready() -> None:
    print(f'Bot started. \nUsername: {bot.user.name}. \nID: {bot.user.id}')
    try:
        await bot.change_presence(activity=config.activity(), status=config.status())
        print(f'{bot.user} has connected to Discord!')
    except InvalidArgument as e:
        print(f'Error changing presence. Exception - {e}')

@bot.event
async def on_connect():
    config.load_cogs(bot)

if __name__ == '__main__':
    try:
        bot.run(BOT_TOKEN)
    except Exception as e:
        print(f'Error starting bot. Exception - {e}')