import asyncio
from enum import IntEnum

import discord
import time
from discord import ApplicationContext, Embed, Guild, Interaction, VoiceClient
from embeds.general import error_embed, succes_embed

import embeds.musical as musical
from modules.music.tune import Tune


YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True', 'quiet': 'True'}


class Loopmode(IntEnum):
    noloop = 0
    song = 1
    queue = 2


class MusicPlayer():

    quiet = False
    loop = Loopmode.noloop

    url = "str"
    queue: list[Tune] = []
    guild: Guild = None
    channel = None

    join_task: asyncio.Future = None

    async def toggle_quiet(self, app_ctx: ApplicationContext):
        if (not self.quiet):
            await app_ctx.response.send_message(ephemeral=True, embed=succes_embed("Enabled quiet mode"))
        else:
            await app_ctx.response.send_message(ephemeral=True, embed=succes_embed("Disabled quiet mode"))

        self.quiet = not self.quiet

    async def next(self):
        if (self.loop == Loopmode.queue and self.queue):
            self.queue.append(self.queue.pop(0))
        elif (self.loop == Loopmode.noloop and self.queue):
            self.queue.pop(0)
        if (not self.queue):
            await self.guild.voice_client.disconnect()
            return
        await self.play()

    async def add_song(self, song: Tune, app_ctx: ApplicationContext):
        if (app_ctx):
            self.guild = app_ctx.guild

        if (not self.guild.voice_client):
            self.channel = app_ctx.channel
            self.join_task = asyncio.create_task(
                app_ctx.user.voice.channel.connect()
            )

        await song.start_load()
        if (len(self.queue) > 0):
            await app_ctx.response.send_message(ephemeral=True, embed=musical.queue_embed(song))
            if (len(self.queue) > 1):
                await self.queue[1].start_load()

        self.queue.append(song)

        if (not self.guild.voice_client or not self.guild.voice_client.is_playing()):
            await self.play(app_ctx)

    async def add_song_bulk(self, song_list: list[Tune], interaction: Interaction):
        if (interaction):
            self.guild = interaction.guild

        await interaction.response.send_message(ephemeral=True, embed=musical.added_song_embed(len(song_list)))
        self.queue += song_list

        if (len(self.queue) > 1):
            await self.queue[1].start_load()

        if (not self.guild.voice_client):
            self.channel = interaction.channel
            self.join_task = asyncio.create_task(
                interaction.user.voice.channel.connect()
            )

        if (not self.guild.voice_client or not self.guild.voice_client.is_playing()):
            await self.play()

    async def play(self, event: ApplicationContext = None):
        def after_song(arg):
            asyncio.run_coroutine_threadsafe(
                self.next(), self._bot_event_loop).result()

        await self.queue[0].create_source()
        if (self.join_task):
            await self.join_task
            self.join_task = None

        self.guild.voice_client.play(
            await self.queue[0].get_source(), after=after_song)

        if (not self.quiet):
            if (event):
                await event.response.send_message(embed=musical.music_embed(self.queue[0]))
            else:
                await self.channel.send(embed=musical.music_embed(self.queue[0]))

        print(
            f"Server: {self.guild}\n[*] The bot is now playing '{self.queue[0].name}' in {self.guild.voice_client.channel}")

        if (len(self.queue) > 1):
            await self.queue[1].start_load()

    async def leave(self):
        self.queue.clear()
        self.loop = Loopmode.noloop
        if (self.guild and self.guild.voice_client.is_playing()):
            self.guild.voice_client.stop()

    async def skip(self):
        if (self.guild and self.guild.voice_client.is_playing()):
            old_loopmode = self.loop
            self.loop = Loopmode.noloop
            self.guild.voice_client.stop()
            self.loop = old_loopmode
            return True
        return False

    async def pause(self):
        if (self.guild.voice_client.is_playing()):
            self.guild.voice_client.pause()
            return True
        return False

    async def unpause(self):
        if (not self.guild.voice_client.is_playing()):
            self.guild.voice_client.resume()
            return True
        return False

    def __init__(self, _bot_event_loop: asyncio.AbstractEventLoop, song: list = None):
        self._bot_event_loop = _bot_event_loop
        if (song):
            self.queue.append(song)
