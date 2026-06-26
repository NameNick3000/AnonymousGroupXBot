import Bot
import Bot1
import Bot3
import asyncio
import datetime
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


async def main():
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(Bot.router)
    dp2 = Dispatcher(storage=MemoryStorage())
    dp2.include_router(Bot1.router)
    dp3 = Dispatcher(storage=MemoryStorage())
    dp3.include_router(Bot3.router)
    await asyncio.wait([
        asyncio.create_task(dp.start_polling(Bot.bot.bots[0])),
        asyncio.create_task(dp2.start_polling(Bot.bot.bots[1])),
        asyncio.create_task(dp3.start_polling(Bot.bot.bots[2]))
    ])


try:
    Bot.connect()
    print("\nStart!\n")
    asyncio.run(main())
except Exception as ex:
    print(f"{datetime.datetime.now()} ex: {ex}")
except KeyboardInterrupt:
    pass
print("\nStop!\n")
