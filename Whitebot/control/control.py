import asyncio
import threading

import discord

class WhiteControl:

    guild: discord.Guild = None
    guilds: list[discord.Guild] = []
    channel: discord.abc.GuildChannel = None
    run: bool = True
    main_thread: threading.Thread = None
    bot: discord.Bot = None

    def load_guilds(self):
        self.bot.fetch_guilds()
        guilds: list[discord.Guild] = self.bot.guilds
        self.guilds = guilds

    def swap_guild(self, guild_name):
        for guild in self.guilds:
            if(guild.name == guild_name):
                self.guild = guild
                print("[*] Succesfully swapped guild")
                self.channel = None
                return
        print(f"[!] Failed to find the guild {guild_name}")

    def swap_channel(self, channel_name):
        if(not self.guild):
            print("[!] No guild is currently set")
            return
        asyncio.run_coroutine_threadsafe(self.guild.fetch_channels(), self.bot.loop).result()
        for channel in self.guild.channels:
            if(channel.name == channel_name):
                self.channel = self.bot.get_channel(channel.id)
                print("[*] Succesfully swapped channel")
                return
        if(self.guild.channels):
            print(f"[*] Failed to swap channel, defaulted to {self.guild.channels[0]}")
        else:
            print("[!] The current guild has no channels")

    def send_message(self, message):
        if(not self.guild):
            print("[!] No guild is currently set")
            return
        if(not self.channel):
            print("[!] No channel is currently set")
            return
        if(not self.channel.can_send()):
            print("[!] The bot is not allowed to send a message in this channel")
            return
        asyncio.run_coroutine_threadsafe(self.channel.send(message), (self.bot.loop)).result()

    def list_guilds(self):
        for guild in self.bot.guilds:
            print(guild.name)
    
    def list_channels(self):
        asyncio.run_coroutine_threadsafe(self.guild.fetch_channels(), self.bot.loop).result()
        for channel in self.guild.channels:
            print(channel.name)

    def parse(self, command):
        args=command.split(" ")
        match(args[0]):
            case "select":
                if(args[1] == "guild"):
                    self.swap_guild(command.removeprefix("select guild "))
                if(args[1] == "channel"):
                    self.swap_channel(command.removeprefix("select channel "))
            case "send":
                self.send_message(command.removeprefix("send "))
            case "refresh":
                self.load_guilds()
            case "list":
                if(args[1] == "guilds"):
                    self.list_guilds()
                if(args[1] == "channels"):
                    self.list_channels()


    def main_loop(self):
        while self.run:
            try:
                channel_name = self.channel.name if self.channel else "none"
                guild_name = self.guild.name if self.guild else "none"
                command = input(f"{guild_name}/{channel_name}>")
                self.parse(command)
            except KeyboardInterrupt:
                self.run = False
            except Exception as e:
                print(f"[!] An unknown error occured {e}")

    def __init__(self, bot):
        self.main_thread = threading.Thread(target=self.main_loop)
        self.main_thread.start()
        self.bot = bot

