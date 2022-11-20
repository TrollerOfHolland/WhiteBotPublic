import asyncio
from youtube_dl import YoutubeDL
from discord import FFmpegOpusAudio, FFmpegPCMAudio, User

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True', 'quiet': 'True'}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -loglevel warning'}


class Tune:

    name: str = ''
    channel_name: str = ''
    video_url: str = ''
    source: FFmpegOpusAudio = None
    source_url: str = ''
    source_path: str = ''
    thumbnail_url: str = ''
    duration: str = ''
    description: str = ''
    loaded: bool = False
    is_raw: bool = False
    source_future: asyncio.Future = None
    requested_by: User = None

    def __init__(self, result) -> None:
        if (not result):
            return
        self.name = result['title']
        self.channel_name = result["channel"]["name"]
        self.video_url = result['link']
        self.thumbnail_url = result["thumbnails"][0]["url"]
        self.duration = result["duration"]
        self.description = result["accessibility"]["title"]

    async def _load_source(self):
        if (not self.loaded and not self.is_raw):
            self.source_url = YoutubeDL(YDL_OPTIONS).extract_info(
                url=self.video_url, download=False)['formats'][0]['url']
            self.loaded = True

        return self.source_url

    async def get_source(self) -> str:
        if (self.source):
            return self.source

        if (not self.source_future):
            return (await self._load_source())

        return await self.source_future

    async def start_load(self) -> asyncio.Future:
        source_future = asyncio.create_task(self._load_source())

    async def create_source(self) -> FFmpegOpusAudio:
        if (not self.is_raw):
            self.source = FFmpegOpusAudio(
                await self.get_source(), **FFMPEG_OPTIONS)
        else:
            self.source = FFmpegPCMAudio(
                self.source_path)

        return self.source

    def to_json(self):
        return vars(self)

    @staticmethod
    def from_json(json):
        tune = Tune(None)
        for key in json:
            setattr(tune, key, json[key])

        return tune
