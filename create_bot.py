from aiogram import Bot


class Bots:
    def __init__(self, tokens: list, parse_mode: str):
        self.bots = [Bot(t, parse_mode=parse_mode) for t in tokens]

    async def send_message(self, *args, **kwargs):
        for bot in self.bots:
            try:
                res = await bot.send_message(*args, **kwargs)
                return res
            except Exception:
                pass
        raise

    async def send_audio(self, *args, **kwargs):
        for bot in self.bots:
            try:
                res = await bot.send_audio(*args, **kwargs)
                return res
            except Exception:
                pass
        raise

    async def send_voice(self, *args, **kwargs):
        for bot in self.bots:
            try:
                res = await bot.send_voice(*args, **kwargs)
                return res
            except Exception:
                pass
        raise

    async def send_photo(self, *args, **kwargs):
        for bot in self.bots:
            try:
                res = await bot.send_photo(*args, **kwargs)
                return res
            except Exception:
                pass
        raise

    async def send_video(self, *args, **kwargs):
        for bot in self.bots:
            try:
                res = await bot.send_video(*args, **kwargs)
                return res
            except Exception:
                pass
        raise

    async def send_sticker(self, *args, **kwargs):
        for bot in self.bots:
            try:
                res = await bot.send_sticker(*args, **kwargs)
                return res
            except Exception:
                pass
        raise

    async def download(self, *args, **kwargs):
        for bot in self.bots:
            try:
                res = await bot.download(*args, **kwargs)
                return res
            except Exception:
                pass
        raise

    async def delete_message(self, *args, **kwargs):
        for bot in self.bots:
            try:
                res = await bot.delete_message(*args, **kwargs)
                return res
            except Exception:
                pass
        raise
