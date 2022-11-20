from discord.ui import Button, View, Modal, InputText
from discord import ApplicationContext, Interaction, ButtonStyle, InputTextStyle

import asyncio
import discord
from embeds.general import error_embed,  succes_embed
from embeds.moderation import vote_embed

from embeds.moderation import no_roles_embed, role_embed
from modules.moderation.permcheck import verify_interaction


class VotingOption(Button):

    parent = None
    option_name: str = None

    async def callback(self, interaction: Interaction):
        await self.parent.register_vote(self.option_name, interaction)

    def __init__(self, parent, button_name: str):
        super().__init__(style=ButtonStyle.secondary, label=button_name)
        self.parent = parent
        self.option_name = button_name


class VoteMenu(View):

    ctx: ApplicationContext = None
    modal: Modal = None
    message: discord.Message = None
    options: list[str] = []
    embed: discord.Embed
    votes: dict[int, str] = {}

    async def send(self):
        self.embed.fields
        await self.ctx.response.send_message(embed=self.embed, view=self, ephemeral=False)

    async def update(self, interaction: Interaction):
        await interaction.response.edit_message(embed=self.embed, view=self)

    def modify_field_value(self, option_name: str, val: int):
        for embed_field in self.embed.fields:
            if (embed_field.name == option_name):
                embed_field.value = str(int(embed_field.value) + val)

    async def register_vote(self, option_name: str, interaction: Interaction):
        if (interaction.user.id in self.votes):
            await interaction.response.send_message(embed=error_embed("You have already voted"), ephemeral=True)
            return
        self.modify_field_value(option_name, 1)
        self.votes[interaction.user.id] = option_name
        await self.update(interaction)
        pass

    @discord.ui.button(label="add option", style=ButtonStyle.blurple, row=2, )
    async def add_option(self, button: Button, interaction: Interaction):
        if (not await verify_interaction(self.ctx, interaction)):
            return

        async def create_option(interaction: Interaction):
            option_name = self.modal.children[0].value
            if (option_name in self.options):
                await interaction.response.send_message(embed=error_embed("An option with that name alread exists"), ephemeral=True)
                return
            self.options.append(option_name)
            self.embed.add_field(name=option_name, value=0)
            button = VotingOption(self, option_name)
            self.add_item(button)
            await self.update(interaction)

        self.modal = Modal(title="Adding a voting option")
        self.modal .add_item(
            InputText(
                label="Option name",
                value="",
                style=InputTextStyle.short
            )
        )
        self.modal .callback = create_option
        await interaction.response.send_modal(self.modal)

    @discord.ui.button(label="Remove my vote", style=ButtonStyle.danger, row=2)
    async def remove_vote(self, button: Button, interaction: Interaction):
        if (interaction.user.id not in self.votes):
            await interaction.response.send_message(embed=error_embed("You have not voted"), ephemeral=True)
            return
        self.modify_field_value(self.votes.pop(interaction.user.id), -1)
        await self.update(interaction)

    @discord.ui.button(label="Stop vote", style=ButtonStyle.danger, row=2)
    async def stop_vote(self, button: Button, interaction: Interaction):
        pass

    def __init__(self, ctx: ApplicationContext, vote_name: str):
        super().__init__(timeout=0)
        self.embed = vote_embed(vote_name)
        self.ctx = ctx


voting_menus: list[int, VoteMenu] = {}
