from aiogram import types
from aiogram.utils.markdown import hbold, hlink, quote_html

from ..misc import dp


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(
        (
            "Привет, {user}!\n"
            "Отправь мне фографию, и я скажу, насколько люди на ней пидоры."
        ).format(user=message.from_user.full_name)
    )
