import discord
from helpers.config import STAFF_ROLES, NORMAL_ROLES

def staff_roles() -> str:
    """
    Function returns tuple of staff roles
    :return:
    """
    staff_roles = tuple(STAFF_ROLES)
    return staff_roles

def normal_roles() -> str:
    """
    Function returns tuple of normal roles
    :return:
    """
    normal_roles = tuple(NORMAL_ROLES)
    return normal_roles