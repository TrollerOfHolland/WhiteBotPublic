from enum import IntEnum

import discord


class LogLevel(IntEnum):
    verbose = 0
    warning = 1
    error = 2


class WhiteLogger:
    path: str = None
    loglevel: LogLevel = LogLevel.verbose

    def log(self, error: discord.DiscordException):
        print(error)
        with open(self.path, 'a') as logfile:
            logfile.write(str(error) + "\n")

    def __init__(self, path: str = "log.txt"):
        self.path = path
