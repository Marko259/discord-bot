import discord
import asyncio

class Youtube(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5) -> None:
        """
        Create Youtube Object
        """
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ''
    
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False, ytdl=None) -> None:
        """
        Get video info from url
        """
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename