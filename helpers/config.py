import discord
import os
from dotenv import load_dotenv
from distutils.util import strtobool

load_dotenv('.env')

DESCRIPTION = 'A Discord bot that allows you to manage your server.'
PRESENCE_TEXT = 'You sleep'

COGS = [
    'cogs.admin',
    'cogs.members',
]

COGS_LOAD = {
    'admin': 'cogs.admin',
    'members': 'cogs.members',
}

STAFF_ROLES = [
    'omnipotent god (på denne server)',
    'Markus the Markus',
    'når man MARKUS'
]

NORMAL_ROLES = [
    'Mennesker'
]

DEBUG = bool(strtobool(str(os.getenv('DEBUG', 'False'))))

BOT_TOKEN = str(os.getenv('BOT_TOKEN'))

GUILD_ID = int(os.getenv('GUILD_ID'))

PATRICK_ID = int(os.getenv('PATRICK_ID'))

PATTE = '<@' + str(PATRICK_ID) + '>'

def activity() -> discord.Activity:
    return discord.Activity(name=PRESENCE_TEXT, type=discord.ActivityType.watching)

def status() -> discord.Status:
    return discord.Status.online

def load_cogs(bot: discord.ext.commands.Bot) -> None:
    for cog in COGS:
        try:
            bot.load_extension(cog)
            print(f'Loaded {cog}')
        except Exception as e:
            print(f'Failed to load extension {cog}. \n Error: {e}')