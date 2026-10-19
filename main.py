import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

TOKEN = os.getenv("BOT_TOKEN", "8939155246:AAEjwhaqWIhTRYzQLcxCnIRZ557_AZe97qo")

kurslar = {
    "python": ("Python", "4 oy", "800 000 so'm"),
    "web": ("Web dasturlash", "6 oy", "1 000 000 so'm"),
    "frontend": ("Frontend", "5 oy", "900 000 so'm"),
    "dizayn": ("Grafik dizayn", "3 oy", "700 000 so'm"),
}

BEKOR = "Bekor qilish"

dp = Dispatcher()


class Yozilish(StatesGroup):
    ism = State()
    telefon = State()
    kurs = State()
    tasdiq = State()


asosiy_menyu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Kurslar"), KeyboardButton(text="Kursga yozilish")],
        [KeyboardButton(text="Markaz haqida"), KeyboardButton(text="Aloqa")],
    ],
    resize_keyboard=True,
)

bekor_menyu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=BEKOR)]], resize_keyboard=True
)


def kurslar_tugmalari(prefiks):
    qatorlar = [
        [InlineKeyboardButton(text=nom, callback_data=f"{prefiks}:{kalit}")]
        for kalit, (nom, _, _) in kurslar.items()
    ]
    if prefiks == "tanla":
        qatorlar.append([InlineKeyboardButton(text=BEKOR, callback_data="bekor")])
    return InlineKeyboardMarkup(inline_keyboard=qatorlar)


tasdiq_tugmalari = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=" Tasdiqlash", callback_data="tasdiqlash"),
            InlineKeyboardButton(text=BEKOR, callback_data="bekor"),
        ]
    ]
)


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Assalomu alaykum! Najot Ta'lim o'quv markazimiz botiga xush kelibsiz",
        reply_markup=asosiy_menyu,
    )


@dp.message(F.text == "Markaz haqida")
async def markaz_haqida(message: Message):
    await message.answer(
        "Markazimiz 2018-yildan beri IT sohasida zamonaviy bilim beradi "
        "Tajribali ustozlar va amaliy darslar"
    )


@dp.message(F.text == "Aloqa")
async def aloqa(message: Message):
    await message.answer("+998 90 123 45 67\n FERGANA sh.\n @oquv_markazi\nIsh vaqi: 8:00 dan 21:00 gacha!")


@dp.message(F.text == "Kurslar")
async def kurslar_royxati(message: Message):
    await message.answer("Kursni tanlang:", reply_markup=kurslar_tugmalari("kurs"))


@dp.callback_query(F.data.startswith("kurs:"))
async def kurs_haqida(callback: CallbackQuery):
    nom, davomiylik, narx = kurslar[callback.data.split(":")[1]]
    await callback.message.answer(
        f"📚 Kurs: {nom}\n⏳ Davomiyligi: {davomiylik}\n💰 Narxi: {narx}"
    )
    await callback.answer()


@dp.message(Command("cancel"))
@dp.message(F.text == BEKOR)
async def bekor_matn(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Yozilish bekor qilindi.", reply_markup=asosiy_menyu)


@dp.callback_query(F.data == "bekor")
async def bekor_tugma(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Yozilish bekor qilindi.", reply_markup=asosiy_menyu)
    await callback.answer()


@dp.message(F.text == "Kursga yozilish")
async def yozilish_boshlash(message: Message, state: FSMContext):
    await state.set_state(Yozilish.ism)
    await message.answer("Ism va familiyangizni kiriting:", reply_markup=bekor_menyu)


@dp.message(Yozilish.ism, F.text)
async def ism_qabul(message: Message, state: FSMContext):
    await state.update_data(ism=message.text)
    await state.set_state(Yozilish.telefon)
    await message.answer("Telefon raqamingizni yuboring (masalan, +998901234567):")


@dp.message(Yozilish.telefon, F.text)
async def telefon_qabul(message: Message, state: FSMContext):
    await state.update_data(telefon=message.text)
    await state.set_state(Yozilish.kurs)
    await message.answer("Kursni tanlang:", reply_markup=kurslar_tugmalari("tanla"))


@dp.callback_query(Yozilish.kurs, F.data.startswith("tanla:"))
async def kurs_tanlash(callback: CallbackQuery, state: FSMContext):
    nom = kurslar[callback.data.split(":")[1]][0]
    await state.update_data(kurs=nom)
    malumot = await state.get_data()
    await state.set_state(Yozilish.tasdiq)
    await callback.message.answer(
        "Ma'lumotlaringizni tekshiring:\n\n"
        f"👤 Ism: {malumot['ism']}\n"
        f"📞 Telefon: {malumot['telefon']}\n"
        f"📚 Kurs: {malumot['kurs']}",
        reply_markup=tasdiq_tugmalari,
    )
    await callback.answer()


@dp.callback_query(Yozilish.tasdiq, F.data == "tasdiqlash")
async def tasdiqlash(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "Arizangiz qabul qilindi! Tez orada siz bilan bog'lanamiz.",
        reply_markup=asosiy_menyu,
    )
    await callback.answer()


async def main():
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())