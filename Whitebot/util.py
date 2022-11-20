from calendar import c
import time
import threading
import json

# This file is a joke and should be removed in the near future

from io import BytesIO
# from PIL import Image
from asgiref.sync import async_to_sync

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True', 'quiet': 'True'}

# backend commands


async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()


def load_json(file):
    json_file = open(file)
    data = json.load(json_file)
    json_file.close()
    return data

# def getImageColor(url):
#     request = requests.get(url)
#     img = Image.open(BytesIO(request.content))
#     img = img.resize((1, 1))
#     color = img.getpixel((0, 0))
#     print(color)
#     return color


async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()
    return (ctx.guild.voice_client)

# client commands


@ async_to_sync
async def message(channel, content):
    await channel.send(content)


class counter:

    def stop(self):
        self.running = False
        return (self.time_passed)

    def count(self):
        self.running = True
        self.time_passed = 0
        while self.running:
            self.time_passed += 1
            time.sleep(1)

    def __init__(self):
        threading.thread(self.count).start()
