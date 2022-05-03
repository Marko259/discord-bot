from email import message
import discord
from discord import InvalidArgument
from discord.utils import get
from discord_slash import SlashCommand
from discord.ext import commands
from dotenv import load_dotenv
from helpers import config
from helpers.config import BOT_TOKEN, DEBUG, PATTE, GUILD_ID, SKAMME
from helpers.database import db_connection

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
async def on_message(message) -> None:
    if DEBUG == False:
        if '@' in message.content:
            await message.channel.send(PATTE)

@bot.event
async def on_raw_reaction_add(payload) -> None:
    if DEBUG == True:
        if payload.guild_id == GUILD_ID:
            mydb = db_connection()
            cursor = mydb.cursor()
            cursor.execute("SELECT * FROM vote2kick WHERE message_id = %s and guild_id = %s", (payload.message_id, payload.guild_id))
            row = cursor.fetchone()
            if payload.emoji.name == '✅' and row is not None:
                channel = bot.get_channel(int(payload.channel_id))
                message = await channel.fetch_message(int(row[3]))
                reaction = get(message.reactions, emoji=payload.emoji.name)
                print(reaction.count)
                react_count = reaction.count
                if react_count >= 1:
                    guild = bot.get_guild(payload.guild_id)
                    member = guild.get_member(int(row[2]))
                    vc = discord.utils.get(guild.text_channels, name=f'{member}')
                    await member.move_to(952326358804090910)
                    cursor.execute("DELETE FROM vote2kick WHERE message_id = %s and guild_id = %s", (payload.message_id, payload.guild_id))
                    mydb.commit()
                
    

        
@bot.event
async def on_connect():
    config.load_cogs(bot)

if __name__ == '__main__':
    try:
        bot.run(BOT_TOKEN)
    except Exception as e:
        print(f'Error starting bot. Exception - {e}')