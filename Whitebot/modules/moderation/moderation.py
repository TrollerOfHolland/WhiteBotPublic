import discord
from discord import Member, Role
from discord.ext import commands
from discord.guild import Guild
from discord.commands.context import ApplicationContext
from embeds.general import succes_embed, error_embed, info_embed
from modules.moderation.roles import RoleMenu
from modules.moderation.voting import VoteMenu
import modules.moderation.voting as voting

from modules.moderation.server_manager import ServerManager
import datetime

from config import GUILD_IDS

server_manager = ServerManager()
role_menus: dict[int, RoleMenu] = {}
vote_menus: dict[int, VoteMenu] = {}
user_timeout: dict[int, datetime.datetime] = {}
voting.voting_menus = vote_menus


class ModerationCommands(commands.Cog):

    def __init__(self, parent_bot: discord.bot):
        self.bot = parent_bot

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            if (not server_manager.does_guild_exist(guild.id)):
                server_manager.add_guild(guild)
            server_manager.correct_roles(guild.id, guild.roles)

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        onjoin_roles = server_manager.get_onjoin_roles(member.guild.id)
        for role in onjoin_roles:
            discord_role = member.guild.get_role(int(role))
            await member.add_roles(discord_role)

    @commands.slash_command(guild_ids=GUILD_IDS, description='Open the role menu to pick and remove your roles')
    async def roles(self, ctx: ApplicationContext):
        if (ctx.author.id in role_menus):
            await role_menus[ctx.author.id].Close()
        short_roles = server_manager.get_available_roles(ctx.guild.id)
        roles: list[Role] = []
        role_icons: dict[str, str] = {}
        for role_id in short_roles:
            roles.append(ctx.guild.get_role(int(role_id)))
            role_icons[str(role_id)] = server_manager.get_role_icon(
                ctx.guild.id, role_id)
        role_menus[ctx.author.id] = RoleMenu(ctx, roles, role_icons)
        await role_menus[ctx.author.id].send()

    @commands.slash_command(guild_ids=GUILD_IDS, description='Add a role that any user can get using the \"/role\" menu, requires the \"Administrator\" privilege')
    async def add_available_role(self, ctx: ApplicationContext, *, name: str):
        if not ctx.author.guild_permissions.administrator:
            ctx.response.send_message(ephemeral=True, embed=error_embed(
                "You do not have the permissions to use this command"))
            return
        role_id = server_manager.get_role_id_by_name(ctx.guild.id, name)
        if (role_id == -1):
            await ctx.response.send_message(ephemeral=True, embed=error_embed("That role could not be found"))
            return
        role = ctx.guild.get_role(role_id)
        if (server_manager.add_available_role(ctx.guild.id, role)):
            await ctx.response.send_message(ephemeral=True, embed=succes_embed("Added available role"))
        else:
            await ctx.response.send_message(ephemeral=True, embed=error_embed("That role was already added to available roles"))

    @commands.slash_command(guild_ids=GUILD_IDS, description='Remove a role that any user can get using the \"/role\" menu, requires the \"Administrator\" privilege')
    async def remove_available_role(self, ctx: ApplicationContext, *, name: str):
        if not ctx.author.guild_permissions.administrator:
            ctx.response.send_message(ephemeral=True, embed=error_embed(
                "You do not have the permissions to use this command"))
            return
        role_id = server_manager.get_role_id_by_name(ctx.guild.id, name)
        if (role_id == -1):
            await ctx.response.send_message(ephemeral=True, embed=error_embed("That role could not be found"))
            return
        role = ctx.guild.get_role(role_id)
        if (server_manager.rem_available_role(ctx.guild.id, role)):
            await ctx.response.send_message(ephemeral=True, embed=succes_embed("Removed available role"))
        else:
            await ctx.response.send_message(ephemeral=True, embed=error_embed("That role is not in available roles"))

    @commands.slash_command(guild_ids=GUILD_IDS, description='Add a role that will be given to a user upon joining, requires the \"Administrator\" privilege')
    async def add_onjoin_role(self, ctx: ApplicationContext, *, name: str):
        if not ctx.author.guild_permissions.administrator:
            ctx.response.send_message(ephemeral=True, embed=error_embed(
                "You do not have the permissions to use this command"))
            return
        role_id = server_manager.get_role_id_by_name(ctx.guild.id, name)
        if (role_id == -1):
            await ctx.response.send_message(ephemeral=True, embed=error_embed("That role could not be found"))
            return
        role = ctx.guild.get_role(role_id)
        if (server_manager.add_onjoin_role(ctx.guild.id, role)):
            await ctx.response.send_message(ephemeral=True, embed=succes_embed("Added onjoin role"))
        else:
            await ctx.response.send_message(ephemeral=True, embed=error_embed("That role was already added to onjoin roles"))

    @commands.slash_command(guild_ids=GUILD_IDS, description='Remove a role that will be given to a user upon joining, requires the \"Administrator\" privilege')
    async def remove_onjoin_role(self, ctx: ApplicationContext, *, name: str):
        if not ctx.author.guild_permissions.administrator:
            ctx.response.send_message(ephemeral=True, embed=error_embed(
                "You do not have the permissions to use this command"))
            return
        role_id = server_manager.get_role_id_by_name(ctx.guild.id, name)
        if (role_id == -1):
            await ctx.response.send_message(ephemeral=True, embed=error_embed("That role could not be found"))
            return
        role = ctx.guild.get_role(role_id)
        if (server_manager.rem_onjoin_role(ctx.guild.id, role)):
            await ctx.response.send_message(ephemeral=True, embed=succes_embed("Removed onjoin role"))
        else:
            await ctx.response.send_message(ephemeral=True, embed=error_embed("That role is not in onjoin roles"))

    @commands.slash_command(guild_ids=GUILD_IDS, description='Add an icon to a role, requires the \"Administrator\" privilege')
    async def add_role_icon(self, ctx: ApplicationContext, *, role_name: str, icon_url: str):
        if not ctx.author.guild_permissions.administrator:
            ctx.response.send_message(ephemeral=True, embed=error_embed(
                "You do not have the permissions to use this command"))
            return
        role_id = server_manager.get_role_id_by_name(ctx.guild.id, role_name)
        if (role_id == -1):
            await ctx.response.send_message(ephemeral=True, embed=error_embed("That role could not be found"))
            return
        server_manager.add_role_icon(ctx.guild.id, role_id, icon_url)
        await ctx.response.send_message(ephemeral=True, embed=succes_embed("Added a role icon"))

    @commands.slash_command(guild_ids=GUILD_IDS, description='Start a vote, requires the \"Administrator\" privilege')
    async def vote(self, ctx: ApplicationContext, *, vote_name: str):
        if not ctx.author.guild_permissions.administrator:
            ctx.response.send_message(ephemeral=True, embed=error_embed(
                "You do not have the permissions to use this command"))
            return
        if (ctx.author.id in vote_menus):
            await ctx.respond("You already have a vote open")
            return
        vote_menus[ctx.author.id] = VoteMenu(ctx, vote_name)
        await vote_menus[ctx.author.id].send()


def setup(bot: discord.bot):
    bot.add_cog(ModerationCommands(bot))
