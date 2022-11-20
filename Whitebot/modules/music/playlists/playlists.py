
from discord.ui import Button, View, Modal, InputText
from discord import ApplicationContext, Interaction, ButtonStyle, InputTextStyle

from embeds.general import *
from embeds.musical import *
from modules.music.tune import Tune
from modules.music.musicplayer import MusicPlayer
from modules.music.youtube_util import get_youtube_url
from modules.music.playlists.playlist_manager import PlaylistManager

from modules.music.verify import check_cmd_interaction


playlist_uis = {}
playlist_manager: PlaylistManager = None


class PlaylistUI(View):

    class deletion_modal(Modal):
        async def send(self, interaction: Interaction):
            await interaction.response.send_modal(self)

        def __init__(self, parent, user_id, playlist_name):
            super().__init__(title="Confirm deletion")
            self.add_item(
                InputText(
                    label="Yes/No",
                    value="",
                    style=InputTextStyle.short
                )
            )
            self.parent = parent
            self.user_id = user_id
            self.playlist_name = playlist_name

        async def callback(self, interaction: Interaction) -> None:
            if (self.children[0].value.lower() == "yes"):
                playlist_manager.delete_playlist(
                    self.user_id, self.playlist_name)
                await interaction.response.send_message(embed=succes_embed("Deleted the playlist"), ephemeral=True)
                await self.parent.close()
            else:
                await self.parent.update_menu(interaction)

    class input_modal(Modal):

        async def send(self, interaction: Interaction):
            await interaction.response.send_modal(self)

        def __init__(self, parent, user_id, playlist_name, index):
            super().__init__(title="Adding a song")
            self.add_item(
                InputText(
                    label="Song name",
                    value="",
                    style=InputTextStyle.short
                )
            )
            self.parent = parent
            self.user_id = user_id
            self.playlist_name = playlist_name
            self.index = index

        async def callback(self, interaction: Interaction) -> None:
            song = get_youtube_url(self.children[0].value)
            playlist_manager.write_song(
                self.user_id, self.playlist_name, song.to_json(), self.index)
            if (self.user_id in playlist_uis):
                playlist_uis[self.user_id].update_playlist()
            self.parent.index = self.index+1
            await self.parent.update_menu(interaction)

    index: int = 0

    async def send(self):
        embed = playlist_entry_embed(
            self.playlist_name, self.playlist[self.index], self.ctx.author) if self.playlist else empty_playlist_embed()
        self.response = await self.ctx.response.send_message(
            embed=embed,
            view=self, ephemeral=False
        )

    def update_playlist(self):
        self.playlist, ret = playlist_manager.get_playlist(
            self.ctx.author.id, self.playlist_name)

    async def update_menu(self, interaction: Interaction):
        self.response = interaction
        self.index = max(min(self.index, len(self.playlist) - 1), 0)
        embed = playlist_entry_embed(
            self.playlist_name, self.playlist[self.index], self.ctx.author) if self.playlist else empty_playlist_embed()
        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    async def close(self):
        playlist_uis.pop(self.ctx.author.id)
        if (self.response):
            await self.response.delete_original_response()

    async def verify_interaction_user(self, interaction: Interaction):
        if (interaction.user.id != self.ctx.author.id):
            await interaction.response.send_message(embed=error_embed(
                "You can not change this playlist"), ephemeral=True)
            return False
        return True

    @ discord.ui.button(style=ButtonStyle.grey, emoji='⏪')
    async def previous_song(self, button: Button, interaction: Interaction):
        if (not await self.verify_interaction_user(interaction)):
            return
        self.index = max(self.index - 1, 0)
        await self.update_menu(interaction)

    @ discord.ui.button(style=ButtonStyle.green, emoji='▶')
    async def play_song(self, button: Button, interaction: Interaction):
        await self.update_menu(interaction)
        if (not await self.verify_interaction_user(interaction)):
            return
        await musicplayers[self.ctx.guild.id].add_song(self.playlist[self.index], self.ctx)

    @ discord.ui.button(style=ButtonStyle.red, emoji='🗑')
    async def remove_song(self, button: Button, interaction: Interaction):
        if (not await self.verify_interaction_user(interaction)):
            return
        playlist_manager.delete_song(
            self.ctx.author.id, self.playlist_name, self.index)
        self.index -= 1
        self.update_playlist()
        await self.update_menu(interaction)

    @ discord.ui.button(style=ButtonStyle.grey, emoji='⏩')
    async def next_song(self, button: Button, interaction: Interaction):
        if (not await self.verify_interaction_user(interaction)):
            return
        self.index = min(self.index + 1, len(self.playlist) -
                         1) if self.playlist else 0
        await self.update_menu(interaction)

    @ discord.ui.button(style=ButtonStyle.blurple, label='Stop editing', emoji='❎')
    async def close_menu(self, button: Button, interaction: Interaction):
        if (not await self.verify_interaction_user(interaction)):
            return
        await self.close()
        await interaction.response.send_message(embed=succes_embed("Closed the editor"), ephemeral=True)

    @ discord.ui.button(label='Play all', style=ButtonStyle.green, row=1, emoji='▶')
    async def play_all(self, button: Button, interaction: Interaction):
        if (not await self.verify_interaction_user(interaction)):
            return

        if (not await check_cmd_interaction(interaction)):
            return

        if (self.playlist):
            await musicplayers[self.ctx.guild.id].add_song_bulk(
                self.playlist, interaction)
        else:
            await interaction.response.send_message(embed=error_embed("This playlist contains no songs"), ephemeral=True)

    @ discord.ui.button(label='Delete all',
                        style=ButtonStyle.red, row=1, emoji='🗑')
    async def remove_all(self, button: Button, interaction: Interaction):
        if (not await self.verify_interaction_user(interaction)):
            return
        self.modal = PlaylistUI.deletion_modal(self,
                                               self.ctx.author.id, self.playlist_name)
        await self.modal.send(interaction)

    @ discord.ui.button(label='Add here',
                        style=ButtonStyle.blurple, row=1)
    async def add_here(self, button: Button, interaction: Interaction):
        if (not await self.verify_interaction_user(interaction)):
            return
        self.modal = PlaylistUI.input_modal(self,
                                            self.ctx.author.id, self.playlist_name, self.index)
        await self.modal.send(interaction)

    @ discord.ui.button(label='Add to end',
                        style=ButtonStyle.blurple, row=1)
    async def add_back(self, button: Button, interaction: Interaction):
        if (not await self.verify_interaction_user(interaction)):
            return
        index = len(self.playlist) - 1 if self.playlist else 0
        self.modal = PlaylistUI.input_modal(
            self, self.ctx.author.id, self.playlist_name, index)
        await self.modal.send(interaction)

    def __init__(self, ctx: ApplicationContext, playlist: list[Tune], playlist_name: str = None):
        super().__init__()
        self.playlist_name = playlist_name
        self.playlist = playlist
        self.ctx = ctx


class PlaylistsUI(View):

    index = 0

    async def close(self):
        await self.response.delete_original_response()

    async def send(self):
        embed = playlists_embed(
            self.playlists[self.index], self.ctx.author)
        self.response = await self.ctx.response.send_message(ephemeral=False,
                                                             embed=embed,
                                                             view=self
                                                             )

    async def update_message(self, interaction: Interaction):
        self.index = max(min(self.index, len(self.playlists) - 1), 0)
        embed = playlists_embed(
            self.playlists[self.index], self.ctx.author)
        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    @ discord.ui.button(style=ButtonStyle.blurple, row=1, emoji='⏮')
    async def previous(self, button: Button, interaction: Interaction):
        self.index -= 1
        await self.update_message(interaction)

    @ discord.ui.button(label='edit', style=ButtonStyle.green, row=1)
    async def edit_playlist(self, button: Button, interaction: Interaction):
        playlist, ret = playlist_manager.get_playlist(
            self.ctx.author.id, self.playlists[self.index])
        playlist_uis[self.ctx.author.id] = PlaylistUI(self.ctx,
                                                      playlist, self.playlists[self.index])
        await playlist_uis[self.ctx.author.id].update_menu(interaction=interaction)

    @ discord.ui.button(style=ButtonStyle.blurple, row=1, emoji='⏭')
    async def next(self, button: Button, interaction: Interaction):
        self.index += 1
        await self.update_message(interaction)

    def __init__(self, ctx: ApplicationContext, playlists: list[str]):
        super().__init__()
        self.ctx = ctx
        self.playlists = playlists


playlist_uis: dict[int, PlaylistUI] = {}
musicplayers: dict[int, MusicPlayer] = {}


def set_playlist_vars(parent_musicplayers, parent_playlist_uis, parent_playlist_manager):
    global musicplayers, playlist_uis, playlist_manager
    musicplayers = parent_musicplayers
    playlist_uis = parent_playlist_uis
    playlist_manager = parent_playlist_manager
