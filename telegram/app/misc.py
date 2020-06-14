from aiogram import Dispatcher, Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.executor import Executor
from . import config

__all__ = ("bot", "dp", "executor", "setup")

bot = Bot(config.TELEGRAM_TOKEN, parse_mode=types.ParseMode.HTML, proxy=config.PROXY_URL)
dp = Dispatcher(bot, storage=MemoryStorage())
executor = Executor(dp)


def setup():
    from . import startup

    executor.on_startup(startup.init_process_pool, polling=True)
    executor.on_shutdown(startup.close_process_pool)

    # noinspection PyUnresolvedReferences
    import app.handlers
