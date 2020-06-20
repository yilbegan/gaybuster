from aiogram import Dispatcher
from concurrent.futures import ProcessPoolExecutor

from . import config


async def init_process_pool(dp: Dispatcher):
    dp["process_pool_executor"] = ProcessPoolExecutor(max_workers=config.MAX_WORKERS)


async def close_process_pool(dp: Dispatcher):
    dp["process_pool_executor"].shutdown(wait=True)
