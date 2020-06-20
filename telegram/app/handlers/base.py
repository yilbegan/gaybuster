from aiogram import types
from html import escape

from ..misc import dp


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer(
        (
            "Привет, {user}!\n"
            "Отправь мне фографию, и я скажу, насколько люди на ней пидоры.\n\n"
            "{site}\n\n"
            "Подписывайтесь на {partia}, {vera} и {anti}!\n"
            "Поддержите отечественную разработку {donate}!"
        ).format(
            user=message.from_user.full_name,
            site=f'<a href="{escape("https://vk.com/partiarobotov")}">Сайт гейдетектора</a>',
            partia=f'<a href="{escape("https://vk.com/partiarobotov")}">ПАРТИЮ</a>',
            vera=f'<a href="{escape("https://vk.com/the_biboran")}">Абдуловеру</a>',
            anti=f'<a href="{escape("https://vk.com/antibezpredel")}">Антибеспредел</a>',
            donate=f'<a href="{escape("http://donatepay.ru/d/vnukelkina")}">донатом</a>',
        )
    )
