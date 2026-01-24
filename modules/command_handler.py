from aiogram.filters import Command,CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from .settings import dispatcher
from .buttons import create_button

@dispatcher.message(CommandStart())
async def start_handler(message:Message, state:FSMContext):
    await state.clear()
    await message.answer(
        text = f"Привiт, {message.from_user.first_name}!\n\nОберiть вашу роль:", 
        reply_markup = create_button(["Учень","Вчитель"])
        )
@dispatcher.message(Command("cancel"))
async def clear_state(message:Message, state:FSMContext):
    await state.clear()
    await message.answer("Дію скасовано. Оберіть вашу роль:", reply_markup = create_button(["Учень","Вчитель"]))

# @dispatcher.message(messag:
# text = message.te
# if text == "help student":
#     returnt.

@dispatcher.message(Command("help"))
async def help_teacher(message:Message, state:FSMContext):
    await state.clear()
    await message.answer("Якщо спочатку ви вибрали кнопку «вчитель», далі потрібно зареєструватися (ввести свій номер телефону, імʼя і пароль), пізніше треба вибрати «створити тест» або «переглянути тест», якщо ви вибрали кнопку «створити тест», вам потрібно вибрати скільки питань хочете щоб було в вашому тесті і також самі питання з варіантами відповідей, а якщо ви вибрали кнопку «переглянути тести» там ви зможете побачити ваші попередні тести які ви робили раніше.") 