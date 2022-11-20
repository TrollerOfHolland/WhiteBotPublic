import discord
from discord import User


from discord.commands.context import ApplicationContext
from modules.music.tune import Tune


def music_embed(song: Tune):
    if (not song.is_raw):
        embed = discord.Embed(
            title="Now playing",
            description=f"[{song.name}]({song.video_url})",
            colour=discord.Colour.blue()
        )
        embed.set_thumbnail(url=song.thumbnail_url)
    else:
        embed = discord.Embed(
            title="Now playing something dubious",
            colour=discord.Colour.blue()
        )

    embed.set_author(
        name="white_bot",
        icon_url="https://cdn.discordapp.com/avatars/862072833004535818/10b5f7da8fa3396ab47d8a9ee4e4b534.png?size=1024"
    )
    return embed


def playlist_entry_embed(playlist_name: str, song: Tune, playlist_author: User):
    embed = discord.Embed(
        title=playlist_name,
        description=f"[{song.name}]({song.video_url})",
        colour=discord.Colour.blue()
    )
    embed.add_field(name=song.channel_name, value=song.description)
    embed.set_thumbnail(url=song.thumbnail_url)
    embed.set_author(
        name=playlist_author.name,
        icon_url=playlist_author.avatar.url
    )
    return embed


def playlists_embed(playlist_name: str, playlist_author: User):
    embed = discord.Embed(
        title=playlist_name,
        colour=discord.Colour.blue()
    )
    embed.set_author(
        name=playlist_author.name,
        icon_url=playlist_author.avatar.url
    )
    return embed


def empty_playlist_embed():
    embed = discord.Embed(
        title="This playlist has no songs",
        colour=discord.Colour.blue()
    )
    embed.set_author(
        name="white_bot",
        icon_url="https://cdn.discordapp.com/avatars/862072833004535818/10b5f7da8fa3396ab47d8a9ee4e4b534.png?size=1024"
    )
    return embed


def queue_embed(song: Tune):
    if (not song.is_raw):
        embed = discord.Embed(title="Song added to the queue:",
                              description=song.description,
                              color=discord.Colour.blue()
                              )
        embed.set_thumbnail(url=song.thumbnail_url)
        embed.add_field(name="Duration:", value=song.duration, inline=True)
    else:
        embed = discord.Embed(title="Added something dubious to the queue:",
                              description=song.description,
                              color=discord.Colour.blue()
                              )
    embed.set_author(
        name="white_bot",
        icon_url="https://cdn.discordapp.com/avatars/862072833004535818/10b5f7da8fa3396ab47d8a9ee4e4b534.png?size=1024"
    )
    return embed


def added_song_embed(amount):
    embed = discord.Embed(title=f"Added {amount} songs to the queue",
                          color=discord.Colour.blue()
                          )
    embed.set_author(
        name="white_bot",
        icon_url="https://cdn.discordapp.com/avatars/862072833004535818/10b5f7da8fa3396ab47d8a9ee4e4b534.png?size=1024"
    )
    return embed


def search_embed(results: list[Tune], rel_index, amount):
    embed = discord.Embed(title="Search results")
    for i in range(1 + rel_index, min(rel_index + amount + 1, len(results))):
        embed.add_field(name=f'{i}: {results[i].channel_name}',
                        value=f"[{results[i].name}]({results[i].video_url})", inline=False)
    embed.set_author(
        name="white_bot",
        icon_url="https://cdn.discordapp.com/avatars/862072833004535818/10b5f7da8fa3396ab47d8a9ee4e4b534.png?size=1024"
    )
    return embed
