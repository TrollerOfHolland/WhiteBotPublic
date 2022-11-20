from discord.ui import Button, View
from discord import ApplicationContext, ButtonStyle
from discord import Interaction
from discord.ext.commands.context import Context
from discord.message import Message

from embeds.general import error_embed
from embeds.musical import search_embed
from modules.music.tune import Tune
from modules.music.verify import check_cmd_interaction


searches = None
musicplayers = None


class SearchButton(Button):

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()
        if (not await check_cmd_interaction(interaction)):
            return
        await musicplayers[self.ctx.guild.id].add_song(self.song, self.ctx)

        await searches.pop(self.ctx.guild.id).close()

    def __init__(self, ctx: Context, song, index: int):
        super().__init__(style=ButtonStyle.primary, label=index)
        self.ctx = ctx
        self.song = song


class SearchResult:

    async def next_results(self, interaction: Interaction) -> None:
        self.res_index = min(self.res_index + self.res_amount,
                             len(self.res) - self.res_amount)
        await interaction.response.edit_message(
            embed=search_embed(self.res, self.res_index, self.res_amount),
            view=self.get_view()
        )

    async def previous_results(self, interaction: Interaction):
        self.res_index = max(self.res_index - self.res_amount, 0)
        await interaction.response.edit_message(
            embed=search_embed(self.res, self.res_index, self.res_amount),
            view=self.get_view()
        )

    def get_view(self) -> list[SearchButton]:
        view = View()
        prev_button = Button(label='<', row=1)
        next_button = Button(label='>', row=1)
        prev_button.callback = self.previous_results
        next_button.callback = self.next_results
        view.add_item(prev_button)
        view.add_item(next_button)
        for index in range(self.res_index, self.res_index + self.res_amount):
            if (index + 1 >= len(self.res)):
                break
            view.add_item(SearchButton(
                self.ctx, self.res[index+1], index+1))

        return view

    async def create_message(self):
        self.message: Message = await self.ctx.respond(
            embed=search_embed(self.res, self.res_index, self.res_amount),
            view=self.get_view()
        )

    def __init__(self, ctx: ApplicationContext, res: list[Tune], results_per_page: int = 8):
        self.ctx: ApplicationContext = ctx
        self.res = res
        self.res_index = 0
        self.res_amount = min(results_per_page, 8)

    async def close(self):
        if (self.message):
            await self.message.delete()


def set_search_vars(parent_musicplayers, parent_searches):
    global musicplayers, searches
    musicplayers = parent_musicplayers
    searches = parent_searches
