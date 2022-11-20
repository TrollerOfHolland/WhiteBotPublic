from discord import ApplicationContext, Interaction, ButtonStyle, Role
import discord
from discord.ui import Button, View
from embeds.general import error_embed

from embeds.moderation import no_roles_embed, role_embed
from modules.moderation.permcheck import verify_interaction


class RoleMenu(View):

    available_roles = []
    index = 0

    async def send(self):
        role_icon = self.role_icons[str(self.available_roles[self.index].id)] if str(
            self.available_roles[self.index].id) in self.role_icons else None
        embed = role_embed(
            self.available_roles[self.index],
            self.available_roles[self.index] in self.ctx.author.roles,
            role_icon
        ) if self.available_roles else no_roles_embed()

        self.response = await self.ctx.response.send_message(
            ephemeral=False,
            embed=embed,
            view=self
        )

    async def Close(self):
        if (self.response):
            try:
                await self.response.delete_original_response()
            except discord.errors.NotFound:
                print(
                    "Whitebot attempt to close a role menu that has already been deleted.")

    async def update_message(self, interaction: Interaction):
        self.index = max(min(self.index, len(self.available_roles) - 1), 0)
        role_icon = self.role_icons[str(self.available_roles[self.index].id)] if str(
            self.available_roles[self.index].id) in self.role_icons else None
        embed = role_embed(
            self.available_roles[self.index],
            self.available_roles[self.index] in self.ctx.author.roles,
            role_icon
        ) if self.available_roles else no_roles_embed()
        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    @discord.ui.button(style=ButtonStyle.blurple, row=1, emoji='⏮')
    async def previous(self, button: Button, interaction: Interaction):
        if (not await verify_interaction(self.ctx, interaction)):
            return
        self.index -= 1
        await self.update_message(interaction)

    @discord.ui.button(label='Toggle', style=ButtonStyle.green, row=1)
    async def toggle(self, button: Button, interaction: Interaction):
        if (not await verify_interaction(self.ctx, interaction)):
            return
        if (not self.available_roles[self.index] in self.ctx.author.roles):
            await self.ctx.author.add_roles(self.available_roles[self.index])
        else:
            await self.ctx.author.remove_roles(self.available_roles[self.index])
        await self.update_message(interaction)

    @discord.ui.button(style=ButtonStyle.blurple, row=1, emoji='⏭')
    async def next(self, button: Button, interaction: Interaction):
        if (not await verify_interaction(self.ctx, interaction)):
            return
        self.index += 1
        await self.update_message(interaction)

    @discord.ui.button(label='Close', style=ButtonStyle.red, row=1)
    async def closebutton(self, button: Button, interaction: Interaction):
        if (not await verify_interaction(self.ctx, interaction)):
            return
        await self.Close()

    def __init__(self, ctx: ApplicationContext, roles: list[Role], role_icons: dict[str, str]):
        super().__init__()
        self.ctx = ctx
        self.available_roles = roles
        self.role_icons = role_icons
