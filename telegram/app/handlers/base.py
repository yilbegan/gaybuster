from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import Throttled
from html import escape

from ..misc import dp
from ..db import Token, User


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


class CreateToken(StatesGroup):
    enter_usages_count = State()


@dp.message_handler(lambda m: m.from_user.id in (498461890,), commands=["create_token"])
async def cmd_create_token(message: types.Message):
    await message.answer("Введите количество использований для токена:")
    await CreateToken.enter_usages_count.set()


@dp.message_handler(state=CreateToken.enter_usages_count)
async def create_token_step_2(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Отправьте число!")
        return

    new_token = Token(usages=int(message.text))
    await new_token.save()
    await message.answer(f"Создан токен на {message.text} использований: <code>{new_token}</code>")
    await state.finish()


@dp.message_handler(regexp=r"[a-z1-9]{7}-[a-z1-9]{4}-[a-z1-9]{4}-[a-z1-9]{4}-[a-z1-9]{12}")
async def activate_token(message: types.Message):
    try:
        await dp.throttle("activate_token", rate=10)
    except Throttled:
        await message.answer(
            "Подождите перед тем как активировать новый токен!"
        )
        return

    token = await Token.filter(token=message.text).first()
    if token is None:
        await message.answer(f"Недействительный ключ!")
        return

    user = await User.filter(user_id=message.from_user.id).first()
    if user is None:
        user = User(user_id=message.from_user.id, usages=token.usages)
    else:
        user.usages += token.usages

    await user.save()
    await token.delete()
    await message.answer(f"Вы активировали ключ на {token.usages} обработок.")
