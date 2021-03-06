import random

from aiogram import types
from aiogram.utils.exceptions import Throttled
from aiohttp import ClientSession, ClientResponse
from tortoise.expressions import F
from io import BytesIO
from html import escape

try:
    import ujson as json
except ImportError:
    import json

from ..utils.photo_utils import prepare_photo
from ..misc import dp
from ..db import User
from .. import config
from uuid import uuid4
from aiofile import AIOFile


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def detect_photo(message: types.Message):
    try:
        await dp.throttle("detect_photo", rate=30)
    except Throttled:
        await message.answer(
            "Подождите пару минут, перед тем как отправлять следующее фото!"
        )
        return

    user = await User.filter(user_id=message.from_user.id).first()
    if user is None:
        user = User(user_id=message.from_user.id)
    elif user.usages <= 0:
        await message.answer("У вас не осталось возможностей обработать фото!")
        return

    user.usages -= 1
    await user.save()

    await message.answer(f"Осталось {user.usages} использований.")

    if random.randint(0, 3) == 2:
        await message.answer(
            "Подписывайтесь на {partia}, {vera} и {anti}!\n"
            "Поддержите отечественную разработку {donate}!".format(
                partia=f'<a href="{escape("https://vk.com/partiarobotov")}">ПАРТИЮ</a>',
                vera=f'<a href="{escape("https://vk.com/the_biboran")}">Абдуловеру</a>',
                anti=f'<a href="{escape("https://vk.com/antibezpredel")}">Антибеспредел</a>',
                donate=f'<a href="{escape("http://donatepay.ru/d/vnukelkina")}">донатом</a>',
            )
        )

    await types.ChatActions.upload_photo()

    photo = BytesIO()
    await message.photo[-1].download(seek=True, destination=photo)
    photo_data = photo.read()
    photo.seek(0)

    async with ClientSession() as session:
        async with session.post(
            config.GAYBUSTER_API_URL, data={"photo": photo}, timeout=185
        ) as request:  # type: ClientResponse
            if request.status >= 400:
                await message.answer("Не удалось распознать фото. Попробуйте позже.")
                return
            result = await request.json()

    if result["count"] == 0:
        await message.answer("Лица на фото не найдены, попробуйте другой ракурс.")
        await User.filter(user_id=message.from_user.id).update(
            balance=F('balance') + 1
        )
        return

    prepared_photo = await dp.loop.run_in_executor(
        dp["process_pool_executor"], prepare_photo, photo_data, result["faces"]
    )

    await message.answer_photo(
        prepared_photo,
        caption=(
            "📕 - Скорее всего гей\n"
            "📙 - Недостаточная точность\n"
            "📗 - Скорее всего не гей\n\n"
            "Гейдетектор может плохо работать на женщинах, а так же на мужчинах младше 18 и старше 50"
        ),
    )

    file_code = str(uuid4())
    async with AIOFile(f"/detections/{file_code}.jpg", "wb") as photo_file:
        await photo_file.write(photo_data)

    async with AIOFile(f"/detections/{file_code}.json", "w") as description_file:
        await description_file.write(json.dumps(result))
