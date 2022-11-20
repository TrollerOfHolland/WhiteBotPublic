import discord
from discord import User


def succes_embed(info: str):
    embed = discord.Embed(
        title=info,
        colour=discord.Colour.green()
    )
    embed.set_author(
        name="white_bot",
        icon_url="https://cdn.discordapp.com/avatars/862072833004535818/10b5f7da8fa3396ab47d8a9ee4e4b534.png?size=1024"
    )
    return embed


def error_embed(error: str):
    embed = discord.Embed(
        title="Error",
        description=error,
        colour=discord.Colour.red()
    )
    embed.set_author(
        name="white_bot",
        icon_url="https://cdn.discordapp.com/avatars/862072833004535818/10b5f7da8fa3396ab47d8a9ee4e4b534.png?size=1024"
    )
    return embed


def info_embed(error: str):
    embed = discord.Embed(
        title="Info",
        description=error,
        colour=discord.Colour.blue()
    )
    embed.set_author(
        name="white_bot",
        icon_url="https://cdn.discordapp.com/avatars/862072833004535818/10b5f7da8fa3396ab47d8a9ee4e4b534.png?size=1024"
    )
    return embed


def usage_embed(usage: str):
    embed = discord.Embed(
        title="Usage",
        description=usage,
        colour=discord.Colour.blue()
    )
    embed.set_author(
        name="white_bot",
        icon_url="https://cdn.discordapp.com/avatars/862072833004535818/10b5f7da8fa3396ab47d8a9ee4e4b534.png?size=1024"
    )
    return embed


def avatar_embed(avatar_url, username):
    embed = discord.Embed(title=username, color=username.color)
    embed.set_image(url=avatar_url)
    embed.description = f"[Download]({avatar_url})"
    embed.set_author(
        name="white_bot",
        icon_url="https://cdn.discordapp.com/avatars/862072833004535818/10b5f7da8fa3396ab47d8a9ee4e4b534.png?size=1024"
    )
    return embed
