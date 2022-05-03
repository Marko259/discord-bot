import re
import discord

from helpers.config import PENIS_COLOR


def embed(description: str = None, colour = None, title: str = None, User = None, author: dict = None, avatar_url: str = None, footer: dict = None, timestamp = None) -> discord.Embed:
    """
    Function returns embeded styled message
    :param title:
    :param description:
    :param colour:
    :param author:
    :param footer:
    :param timestamp:
    :return:
    """
    if colour is None:
        colour = PENIS_COLOR

    if description:
        description = '**Grund**\n' + description + '\n\nReagere med :white_check_mark: på denne besked for at smide <@{User}> i skammekrogen'.format(User=User)
    else:
        description = 'Reagere med :white_check_mark: på denne besked for at smide <@{User}> i skammekrogen'.format(User=User)

    if timestamp:
        embed = discord.Embed(title=title, description=description, colour=colour, timestamp=timestamp)
    else:
        embed = discord.Embed(title=title, description=description, colour=colour)
    
    if author:
        embed.set_author(name=f'{author}', icon_url=avatar_url)
    
    if footer:
        embed.set_footer(text=footer)
    
    return embed