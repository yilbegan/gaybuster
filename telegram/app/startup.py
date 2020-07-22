import asyncpg
import asyncio

from aiogram import Dispatcher
from concurrent.futures import ProcessPoolExecutor
from tortoise import Tortoise
from tortoise.exceptions import DBConnectionError

from . import config


async def init_process_pool(dp: Dispatcher):
    dp["process_pool_executor"] = ProcessPoolExecutor(max_workers=config.MAX_WORKERS)


async def close_process_pool(dp: Dispatcher):
    dp["process_pool_executor"].shutdown(wait=True)


async def init_postgres(dp: Dispatcher):
    while True:
        try:
            await Tortoise.init(
                db_url=config.POSTGRES_CONNECTION_URI, modules={"models": ["app.db"]}
            )
            break
        except (ConnectionRefusedError, asyncpg.CannotConnectNowError, DBConnectionError):
            await asyncio.sleep(1)
    await Tortoise.generate_schemas()


async def close_postgres(dp: Dispatcher):
    await Tortoise.close_connections()
