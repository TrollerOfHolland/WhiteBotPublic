import os

from white_logging import WhiteLogger, LogLevel
from embeds.general import avatar_embed, succes_embed, error_embed

import discord
from discord.ext import commands
from discord.commands.context import ApplicationContext
from control.control import WhiteControl

from config import TOKEN, GUILD_IDS
control_panel: WhiteControl = None

bot = commands.Bot(intents=discord.Intents.all(), command_prefix=";")
bot_modules = ['music.music', 'memes.memes', 'moderation.moderation']

white_logger = WhiteLogger()


@bot.event
async def on_ready():
    control_panel = WhiteControl(bot)
    print("[*] White is ready.")


@bot.event
async def on_application_command_error(ctx: ApplicationContext, error: discord.DiscordException):
    print("[*] An error occurred")
    white_logger.log(error)
    if (not ctx.response.is_done()):
        await ctx.response.send_message(embed=error_embed("An unknown error occurred"), ephemeral=True)


@bot.slash_command(guild_ids=GUILD_IDS, description="Basic ping command")
async def ping(ctx):
    await ctx.response.send_message(embed=succes_embed(f"The bots ping is around {round(bot.latency * 1000 )} ms"), ephemeral=True, )


@ bot.slash_command(guild_ids=GUILD_IDS, description="Displays the user avatar")
async def avatar(ctx: ApplicationContext, *,  member: discord.Member = None):
    if (not member):
        member = ctx.author
    user_avatar_url = member.avatar
    embed = avatar_embed(user_avatar_url, member)
    await ctx.response.send_message(ephemeral=False, embed=embed)


@ bot.command()
async def reload(ctx):
    if (not str(ctx.author) == "Larsy#0498"):
        return
    for module in bot_modules:
        bot.unload_extension(f'modules.{module}')
        bot.load_extension(f'modules.{module}')
    os.system("cls")
    print("extensions reloaded")

for module in bot_modules:
    bot.load_extension(f'modules.{module}')

bot.run(TOKEN)
