import os
import json

from enum import IntEnum
from threading import Lock

from modules.music.tune import Tune


class PlaylistManager():

    mutex = Lock()

    playlists = {}

    class Codes(IntEnum):
        succes = 0

        playlist_already_exists = 101
        playlist_not_found = 102
        index_out_of_range = 103

    def _save(self):
        self.mutex.acquire()
        with open("modules/music/playlists/playlists.json", 'w') as playlists_file:
            json.dump(self.playlists, playlists_file, indent=4)
        self.mutex.release()

    def _add_user(self, user_id) -> bool:
        if (not str(user_id) in self.playlists):
            self.playlists[str(user_id)] = {}
            return True
        return False

    def _playlist_exists(self, user_id: int, playlist_name: str) -> bool:
        self._add_user(user_id)
        return (playlist_name in self.playlists[str(user_id)])

    def create_playlist(self, user_id: int, playlist_name: str) -> int:
        if (self._playlist_exists(user_id, playlist_name)):
            return ([], PlaylistManager.Codes.playlist_already_exists)
        self.playlists[str(user_id)][playlist_name] = {"songs": []}
        self._save()
        return ([], PlaylistManager.Codes.succes)

    def delete_playlist(self, user_id: int, playlist_name: str):
        if (not self._playlist_exists(user_id, playlist_name)):
            return PlaylistManager.Codes.playlist_not_found
        self.playlists[str(user_id)].pop(playlist_name)
        self._save()
        return PlaylistManager.Codes.succes

    def write_song(self, user_id: int, playlist_name: str, song: Tune, index: int) -> int:
        if (not self._playlist_exists(user_id, playlist_name)):
            return PlaylistManager.Codes.playlist_not_found
        self.playlists[str(user_id)][playlist_name]["songs"].insert(
            index+1, song)
        self._save()
        return PlaylistManager.Codes.succes

    def delete_song(self, user_id: int, playlist_name: str, song_index: int) -> int:
        if (not self._playlist_exists(user_id, playlist_name)):
            return PlaylistManager.Codes.playlist_not_found
        if (song_index >= len(self.playlists[str(user_id)][playlist_name]['songs'])):
            return PlaylistManager.Codes.index_out_of_range
        self.playlists[str(user_id)][playlist_name]['songs'].pop(song_index)
        self._save()
        return PlaylistManager.Codes.succes

    def get_playlist(self, user_id: int, playlist_name: str) -> tuple[list[Tune], int]:
        if (not self._playlist_exists(user_id, playlist_name)):
            return ([], PlaylistManager.Codes.playlist_not_found)

        tunes: list[Tune] = []
        for raw_tune in self.playlists[str(user_id)][playlist_name]["songs"]:
            tunes.append(Tune.from_json(raw_tune))
        return (tunes, PlaylistManager.Codes.succes)

    def get_user_playlists(self, user_id: int):
        if (self._add_user(user_id)):
            return {}
        return self.playlists[str(user_id)]

    def get_playlists_by_guild_id(self, guild_id: int):
        result = []
        for user_playlists in self.playlists.values():
            for playlist in user_playlists.values():
                if (playlist["guild_id"] == str(guild_id) and (playlist["visibility"] == "guild" or playlist["visibility"] == "public")):
                    result.append(playlist)
        return result

    def get_public_playlists(self):
        result = []
        for user_playlists in self.playlists.values():
            for playlist in user_playlists.values():
                if (playlist["visibility"] == "public"):
                    result.append(playlist)
        return result

    def __init__(self):
        if (not os.path.exists("modules/music/playlists/playlists.json")):
            self.playlists = {}
            self._save()
        else:
            with open("modules/music/playlists/playlists.json", "r") as playlists_file:
                self.playlists = json.load(playlists_file)
