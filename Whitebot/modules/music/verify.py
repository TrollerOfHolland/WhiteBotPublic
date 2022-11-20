from discord import ApplicationContext, Interaction
from embeds.general import error_embed


async def check_cmd(ctx: ApplicationContext):
    if (not ctx.author.voice):
        await ctx.response.send_message(ephemeral=True, embed=error_embed("You are not in a voice channel"))
        return False
    elif (ctx.guild.voice_client and not ctx.author.voice.channel == ctx.guild.voice_client.channel):
        await ctx.response.send_message(ephemeral=True, embed=error_embed("You are not in the same voice channel as the bot"))
        return False
    return True


async def check_cmd_interaction(interaction: Interaction):
    if (not interaction.user.voice):
        await interaction.response.send_message(ephemeral=True, embed=error_embed("You are not in a voice channel"))
        return False
    elif (interaction.guild.voice_client and not interaction.user.voice.channel == interaction.guild.voice_client.channel):
        await interaction.response.send_message(ephemeral=True, embed=error_embed("You are not in the same voice channel as the bot"))
        return False
    return True
