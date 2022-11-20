from embeds.general import error_embed
from discord import Interaction, ApplicationContext


async def verify_interaction(ctx: ApplicationContext, interaction: Interaction):
    if (ctx.author.id != interaction.user.id):
        await interaction.response.send_message(
            embed=error_embed("You are not allowed to click this button"), ephemeral=True)
        return False
    else:
        return True
