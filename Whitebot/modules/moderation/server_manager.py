import os
import json

from threading import Lock
from enum import Enum
from discord import Guild, Role


class ServerManager:

    mutex = Lock()

    sv_info = {}

    def _save(self):
        self.mutex.acquire()
        with open("modules/moderation/server_data.json", "w") as sv_info_file:
            json.dump(self.sv_info, sv_info_file, indent=4)
        self.mutex.release()

    def does_guild_exist(self, guild_id: int):
        return str(guild_id) in self.sv_info.keys()

    def get_roles(self, guild_id: int):
        return self.sv_info[str(guild_id)]["roles"]

    def get_available_roles(self, guild_id: int):
        return self.sv_info[str(guild_id)]["available_roles"]

    def get_onjoin_roles(self, guild_id: int):
        return self.sv_info[str(guild_id)]["onjoin_roles"]

    def get_role_icon(self, guild_id: int, role_id: int):
        if (str(role_id) in self.sv_info[str(guild_id)]["role_icons"]):
            return self.sv_info[str(guild_id)]["role_icons"][str(role_id)]
        return None

    def add_available_role(self, guild_id: int, role: Role):
        if (not str(role.id) in self.sv_info[str(guild_id)]["available_roles"]):
            self.sv_info[str(guild_id)]["available_roles"][str(
                role.id)] = role.name
            self._save()
            return True
        return False

    def rem_available_role(self, guild_id: int, role: Role):
        if (str(role.id) in self.sv_info[str(guild_id)]["available_roles"]):
            self._save()
            self.sv_info[str(guild_id)]["available_roles"].pop(str(role.id))
            return True
        return False

    def add_onjoin_role(self, guild_id: int, role: Role):
        if (not str(role.id) in self.sv_info[str(guild_id)]["onjoin_roles"]):
            self.sv_info[str(guild_id)]["onjoin_roles"][str(
                role.id)] = role.name
            self._save()
            return True
        return False

    def rem_onjoin_role(self, guild_id: int, role: Role):
        if (str(role.id) in self.sv_info[str(guild_id)]["onjoin_roles"]):
            self._save()
            self.sv_info[str(guild_id)]["onjoin_roles"].pop(str(role.id))
            return True
        return False

    def get_role_name_by_id(self, guild_id: int, role_id: int):
        return self.sv_info[str(guild_id)]["roles"][str(role_id)]

    def get_role_id_by_name(self, guild_id: int, role_name: str):
        for role_id in self.sv_info[str(guild_id)]["roles"]:
            if (self.sv_info[str(guild_id)]["roles"][role_id] == role_name):
                return int(role_id)
        return -1

    def add_guild(self, guild: Guild):
        self.sv_info[str(guild.id)] = {"server_name": guild.name, "roles": {
        }, "onjoin_roles": {}, "available_roles": {}}
        self.sv_info[str(guild.id)]["roles"] = dict(
            zip([a.id for a in guild.roles], [a.name for a in guild.roles]))
        self._save()

    def add_role_icon(self, guild_id: int, role_id, icon_url: str):
        self.sv_info[str(guild_id)]["role_icons"][str(role_id)] = icon_url
        self._save()

    def correct_roles(self, guild_id: int, roles: list[Role]):
        old_roles = self.sv_info[str(guild_id)]["roles"].copy()
        for role in roles:
            if (str(role.id) not in self.sv_info[str(guild_id)]["roles"]):
                self.sv_info[str(guild_id)]["roles"][str(role.id)] = role.name
            elif (role.name != self.sv_info[str(guild_id)]["roles"][str(role.id)]):
                self.sv_info[str(guild_id)]["roles"][str(role.id)] = role.name
                if (str(role.id) in self.sv_info[str(guild_id)]["available_roles"]):
                    self.sv_info[str(guild_id)]["available_roles"][str(
                        role.id)] = role.name
                if (str(role.id) in self.sv_info[str(guild_id)]["onjoin_roles"]):
                    self.sv_info[str(guild_id)]["onjoin_roles"][str(
                        role.id)] = role.name
        role_ids = [a.id for a in roles]
        for role in old_roles:
            if (int(role) not in role_ids):
                self.sv_info[str(guild_id)]["roles"].pop(role)
                if (role in self.sv_info[str(guild_id)]["available_roles"]):
                    self.sv_info[str(guild_id)]["available_roles"].pop(role)
                if (role in self.sv_info[str(guild_id)]["onjoin_roles"]):
                    self.sv_info[str(guild_id)]["onjoin_roles"].pop(role)
        self._save()

    def __init__(self):
        if (not os.path.exists("modules/moderation/server_data.json")):
            self.sv_info = {}
            self._save()
        else:
            with open("modules/moderation/server_data.json", "r") as sv_info_file:
                self.sv_info = json.load(sv_info_file)
