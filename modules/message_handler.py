from .states import Registration,Teacher,Student
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from .settings import dispatcher
from .work_json import read_json
from .buttons import create_button
@dispatcher.message()
async def message_handler(message:Message, state:FSMContext):
    if message.text == "Вчитель":
        users_data = read_json("users.json")
        user_id = message.from_user.id
        if str(user_id) in users_data:
            await message.answer(
                text="Що ви хочете зробити?", 
                reply_markup= create_button(["Створити тест","Переглянути тести"])
            )
            await state.set_state(Teacher.choice)
            
            
        else:
            await message.answer(text="Потрібно зареєструватися")
            await message.answer(text="Напишіть своє ім'я")
            await state.set_state(Registration.name)
    elif message.text == "Учень":
        await message.answer(text="Введіть код тесту:")
        await state.set_state(Student.code)
        

            

            
