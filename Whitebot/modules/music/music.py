import re
import asyncio
import time

import discord
from discord.ext import commands
from discord.guild import Guild
from discord.commands.context import ApplicationContext

from embeds.general import *
from modules.music.tune import Tune
from modules.music.youtube_util import youtube_search, get_youtube_url
from config import GUILD_IDS
from modules.music.musicplayer import MusicPlayer, Loopmode
from modules.music.playlists.playlist_manager import PlaylistManager

from modules.music.search.search import SearchResult, set_search_vars
from modules.music.playlists.playlists import PlaylistUI, PlaylistsUI, set_playlist_vars

from modules.music.verify import check_cmd


searches: dict[int, SearchResult] = {}
playlist_uis: dict[int, PlaylistUI] = {}
musicplayers: dict[Guild, MusicPlayer] = {}
playlist_manager = PlaylistManager()


set_search_vars(musicplayers, searches)
set_playlist_vars(musicplayers, playlist_uis, playlist_manager)


class MusicCommands(commands.Cog):

    def __init__(self, parent_bot: discord.bot):
        self.bot = parent_bot

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            musicplayers[guild.id] = MusicPlayer(self.bot.loop)

    @commands.slash_command(guild_ids=GUILD_IDS, description='Plays a song')
    async def play(self, ctx: ApplicationContext, *, query: str):
        if (await check_cmd(ctx)):
            song = get_youtube_url(query)
            if (not song):
                await ctx.response.send_message(embed=error_embed("Failed to find a song"), ephemeral=True)
                return
            await musicplayers[ctx.guild.id].add_song(song, ctx)

    @commands.slash_command(guild_ids=GUILD_IDS, description='Pause')
    async def pause(self, ctx: ApplicationContext):
        if (await check_cmd(ctx)):
            if (await musicplayers[ctx.guild.id].pause()):
                await ctx.response.send_message(ephemeral=True, embed=succes_embed("⏸ Paused"))
            else:
                await ctx.response.send_message(ephemeral=True, embed=error_embed("The bot is already paused"))

    @ commands.slash_command(guild_ids=GUILD_IDS, description='Unpause', aliases=['continue', 'resume'])
    async def unpause(self, ctx: ApplicationContext):
        if (await check_cmd(ctx)):
            if (await musicplayers[ctx.guild.id].unpause()):
                await ctx.response.send_message(ephemeral=True, embed=succes_embed("▶️ Unpaused"))
            else:
                await ctx.response.send_message(ephemeral=True, embed=error_embed("The bot is already playing"))

    @ commands.slash_command(guild_ids=GUILD_IDS, description='Leave the vc', aliases=['dc', 'shoo', 'stop', 'disconnect'])
    async def stop(self, ctx: ApplicationContext):
        if (await check_cmd(ctx)):
            await musicplayers[ctx.guild.id].leave()
            await ctx.response.send_message(ephemeral=True, embed=succes_embed("Left the vc"))

    @ commands.slash_command(guild_ids=GUILD_IDS, description='Skip the song that is currently playing', aliases=['s'])
    async def skip(self, ctx: ApplicationContext):
        if (await musicplayers[ctx.guild.id].skip()):
            await ctx.response.send_message(ephemeral=True, embed=succes_embed("⏩ Song skipped"))
        else:
            await ctx.response.send_message(ephemeral=True, embed=error_embed("The bot is not playing anything"))

    @ commands.slash_command(guild_ids=GUILD_IDS, description='Searches for a particular song')
    async def search(self, ctx: ApplicationContext, *, query: str = None):
        if (not query):
            await ctx.channel.send(embed=usage_embed(f"To use the `search` command, type `;search 'query'`\n To specify the amount of results that should be shown on a page, use ```amount=n``` where `n` will be the amount of results, up to a maximum of `8`."))
            return

        pattern = r"amount\s?=\s?[0-9]{1,2}"
        match = re.search(pattern, query)
        amount = 4
        if (match):
            query = query.replace(match.group(0), '')
            amount = int(match.group(0).split('=')[1])

        if (query == None):
            await ctx.channel.send(embed=error_embed("Please enter a string to search for"))
            return
        if (not ctx.author.voice):
            await ctx.channel.send(embed=error_embed("You are not in a voice channel"))
            return
        if ctx.guild.id in searches:
            await searches[ctx.guild.id].close()

        result = await youtube_search(query, lim=20)
        if (result == None):
            await ctx.channel.send(embed=error_embed("No results have been found for the given query"))
            return

        searches[ctx.guild.id] = SearchResult(ctx, result, amount)
        await searches[ctx.guild.id].create_message()

    @ commands.slash_command(guild_ids=GUILD_IDS, description='Sets the loopmode for the bot', aliases=['repeat'])
    async def loop(self, ctx: ApplicationContext, *, args: str):
        if (not await check_cmd(ctx)):
            return
        if (args.lower() == "song"):
            if (not musicplayers[ctx.guild.id].loop == Loopmode.song):
                musicplayers[ctx.guild.id].loop = Loopmode.song
                await ctx.response.send_message(embed=succes_embed("Started looping"))
            else:
                musicplayers[ctx.guild.id].loop = Loopmode.noloop
                await ctx.response.send_message(embed=succes_embed("Stopped looping"))
        elif (args.lower() == "queue"):
            if (not musicplayers[ctx.guild.id].loop == Loopmode.queue):
                musicplayers[ctx.guild.id].loop = Loopmode.queue
                await ctx.response.send_message(embed=succes_embed("Started looping the queue"))
            else:
                musicplayers[ctx.guild.id].loop = Loopmode.noloop
                await ctx.response.send_message(embed=succes_embed("Stopped looping the queue"))
        else:
            await ctx.response.send_message(ephemeral=True, embed=succes_embed("Usage: Loop song/queue"))

    async def open_PlaylistUI(self, ctx: ApplicationContext, playlist, name):
        playlist_uis[ctx.author.id] = PlaylistUI(ctx, playlist, name)
        await playlist_uis[ctx.author.id].send()

    @commands.slash_command(guild_ids=GUILD_IDS, description='Create or edit playlists')
    async def playlist(self, ctx: ApplicationContext, *, create_or_edit: str = None, name: str = None):
        if (ctx.author.id in playlist_uis):
            await playlist_uis[ctx.author.id].close()

        if (create_or_edit == None):
            playlists = list(playlist_manager.get_user_playlists(
                str(ctx.author.id)).keys())
            if (not playlists):
                await ctx.response.send_message(ephemeral=True, embed=error_embed("You have no playlists"))
                return
            playlist_uis[ctx.author.id] = PlaylistsUI(ctx, playlists)
            await playlist_uis[ctx.author.id].send()
            return

        if (create_or_edit == 'edit'):
            if (not name):
                await ctx.response.send_message(ephemeral=True, embed=error_embed("No playlist name was provided"))
                return
            playlist, ret = playlist_manager.get_playlist(ctx.author.id, name)
            if (ret == PlaylistManager.Codes.playlist_not_found):
                await ctx.response.send_message(ephemeral=True, embed=error_embed("You do not have a playlist with that name"))
                return
            await self.open_PlaylistUI(ctx, playlist, name)
            return

        if (create_or_edit == 'create'):
            if (not name):
                await ctx.response.send_message(ephemeral=True, embed=error_embed("No playlist name was provided"))
                return
            playlist, ret = playlist_manager.create_playlist(
                ctx.author.id, name)
            if (ret == PlaylistManager.Codes.playlist_already_exists):
                await ctx.response.send_message(embed=error_embed("You already have a playlist with that name"), ephemeral=True)
                return
            await self.open_PlaylistUI(ctx, playlist, name)
            return

    @commands.slash_command(guild_ids=GUILD_IDS, description="Plays the german dub version of \"Thug Hunter with Spencer Reed & Sean Xavier\"")
    async def germanhunting(self, ctx: ApplicationContext):
        song = Tune(None)
        song.source_path = "modules/music/data/hunting_german.mp3"
        song.is_raw = True
        await musicplayers[ctx.guild.id].add_song(song, ctx)

        # @commands.slash_command(guild_ids=GUILD_IDS, description=''))
        # async def clearqueue(self, ctx: ApplicationContext):
        #     if(isPlayerAlive(ctx.guild.id)):
        #         players[ctx.guild.id].queue = [
        #             players[ctx.guild.id].queue[0]]
        #         await ctx.channel.send("Queue cleared")
        #     else:
        #         await ctx.channel.send("The self.bot is not in a vc")

        # @commands.slash_command(guild_ids=GUILD_IDS, description=''))
        # async def shuffle(self, ctx: ApplicationContext):
        #     if(isPlayerAlive(ctx.guild.id)):
        #         random.shuffle(players[ctx.guild.id].queue)

        # @commands.slash_command(guild_ids=GUILD_IDS, description=''), aliases=['np'])
        # async def nowplaying(self, ctx: ApplicationContext):
        #     if(isPlayerAlive(ctx.guild.id)):
        #         await ctx.channel.send(embeds.music_embed(players[ctx.guild.id].queue[0][0]))

        # @commands.slash_command(guild_ids=GUILD_IDS, description=''), aliases=['q'])
        # async def queue(self, ctx: ApplicationContext):
        #     if(isPlayerAlive(ctx.guild.id)):
        #         queueText = "```[*] Queue:\n"
        #         for i in range(len(players[ctx.guild.id].queue)):
        #             queueText += "No. " + \
        #                 str(i+1) + ": " + \
        #                 players[ctx.guild.id].queue[i][1] + "\n"
        #         await ctx.channel.send(queueText + "```")

    @commands.slash_command(guild_ids=GUILD_IDS, description='Makes the bot not output \"Now Playing\" messages')
    async def quiet(self, ctx: ApplicationContext):
        if (await check_cmd(ctx)):
            await musicplayers[ctx.guild_id].toggle_quiet(ctx)
    # @commands.slash_command(guild_ids=GUILD_IDS, description=''))
    # async def move(self, ctx: ApplicationContext):
    #     if(await check_cmd(ctx)):
    #         await ctx.channel.send("The self.bot is not in a voice channel")
    #         return
    #     await musicplayers[ctx.guild.id].move(ctx.message.author.voice.channel)
    #     await ctx.channel.send(f"Moved to `{ctx.message.author.voice.channel}`")


def setup(bot):
    bot.add_cog(MusicCommands(bot))
