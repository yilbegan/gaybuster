from aiogram import types
from aiogram.utils.exceptions import Throttled
from aiohttp import ClientSession, ClientResponse
from io import BytesIO

from ..utils.photo_utils import prepare_photo
from ..misc import dp
from .. import config


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def detect_photo(message: types.Message):
    try:
        await dp.throttle('detect_photo', rate=5)
    except Throttled:
        await message.answer("Подождите, перед тем как отправлять следующее фото!")
        return

    await types.ChatActions.upload_photo()

    photo = BytesIO()
    await message.photo[0].download(seek=True, destination=photo)
    photo_data = photo.read()
    photo.seek(0)
    async with ClientSession() as session:
        async with session.post(config.GAYBUSTER_API_URL, data={'photo': photo}, timeout=45) as request:  # type: ClientResponse
            if request.status >= 400:
                await message.answer('Не удалось распознать фото. Попробуйте позже.')
                return
            result = await request.json()

    if result['count'] == 0:
        await message.answer('Лица на фото не найдены, попробуйте другой ракурс.')
        return

    prepared_photo = await dp.loop.run_in_executor(dp['process_pool_executor'], prepare_photo, photo_data, result['faces'])
    await message.answer_photo(
        prepared_photo,
        caption=(
            "📕 - Скорее всего гей\n"
            "📙 - Недостаточная точность\n"
            "📗 - Скорее всего не гей\n\n"
            "Гейдетектор может плохо работать на женщинах, а так же на мужчинах младше 18 и старше 50"
        )
    )
