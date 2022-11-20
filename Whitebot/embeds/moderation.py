import discord
from discord import Role
from config import BOT_NAME


def role_embed(role:  Role, has_role: bool, role_icon: str):
    embed = discord.Embed(
        colour=role.color
    )
    if (has_role):
        embed.title = "You have this role"
    else:
        embed.title = "You do not have this role"
    if (role_icon):
        embed.set_author(
            name=role.name,
            icon_url=role_icon
        )
    else:
        embed.set_author(
            name=role.name,
            icon_url="https://cdn.discordapp.com/avatars/862072833004535818/10b5f7da8fa3396ab47d8a9ee4e4b534.png?size=1024"
        )

    return embed


def no_roles_embed():
    embed = discord.Embed(
        title="There are no available roles",
        colour=discord.Colour.blue()
    )
    embed.set_author(
        name=BOT_NAME,
        icon_url="https://cdn.discordapp.com/avatars/862072833004535818/10b5f7da8fa3396ab47d8a9ee4e4b534.png?size=1024"
    )
    return embed


def vote_embed(vote_name: str) -> discord.Embed:
    embed = discord.Embed(
        title=vote_name,
        colour=discord.Colour.from_rgb(255, 255, 255)
    )
    embed.set_author(
        name=BOT_NAME,
        icon_url="https://cdn.discordapp.com/avatars/862072833004535818/10b5f7da8fa3396ab47d8a9ee4e4b534.png?size=1024",
    )

    return embed
