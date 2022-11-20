import random

import discord
from discord.ext import commands
from discord.guild import Guild
from discord.commands.context import ApplicationContext

from config import GUILD_IDS


class MemeCommands(commands.Cog):

    dead_russian_tanks = []

    def __init__(self, parent_bot: discord.bot):
        self.bot = parent_bot

    @commands.Cog.listener()
    async def on_ready(self):
        with open("modules/memes/dead_russian_tanks.txt", "r") as f:
            self.dead_russian_tanks = f.readlines()

    @commands.slash_command(guild_ids=GUILD_IDS, description="Shows a random disabled / captured russian tank")
    async def ruski(self, ctx: ApplicationContext):
        await ctx.respond(random.choice(self.dead_russian_tanks))


def setup(bot):
    bot.add_cog(MemeCommands(bot))
