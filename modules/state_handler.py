from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from .states import Registration, Teacher, Student
from .settings import dispatcher
from .work_json import create_json, read_json
from .buttons import create_button, test_buttons
from aiogram.enums import ParseMode

@dispatcher.message(Registration.name)
async def name_handler(message:Message, state:FSMContext):
    await state.update_data(name = message.text)
    await message.answer(text = "Введіть ваш номер телефону:")
    await state.set_state(Registration.phone_number)
    
    
@dispatcher.message(Registration.phone_number)
async def phone_handler(message:Message, state:FSMContext):
    await state.update_data(phone_number = message.text)
    await message.answer(text = "Введіть ваш пароль")
    await state.set_state(Registration.password)


@dispatcher.message(Registration.password)
async def password_handler(message:Message, state:FSMContext):
    await state.update_data(password = message.text)
    
    
    user_data = await state.get_data()
    json_data = read_json("users.json")
    json_data.setdefault(str(message.from_user.id),{
        "name": user_data["name"],
        "phone_number": user_data["phone_number"],
        "password": user_data["password"],
        "tests": []        
    })
    create_json(data = json_data, name_file="users.json")
    await message.answer(text = "Реєстрація завершена!")
    await state.clear()
    
@dispatcher.message(Teacher.choice)
async def choice_handler(message:Message, state:FSMContext):
    if message.text == "Створити тест":
        await message.answer("Скільки питань ?")
        await state.set_state(Teacher.questions_count)

    elif message.text == "Переглянути тести":
        json_data = read_json("users.json")
        info_user = json_data[str(message.from_user.id)]
        tests:list = info_user["tests"]
        for test in tests:
            test: list = test
            test_message = ""
            question_message = ""

            for question in test:
                test_message += "\n\n═══════════════════════════════\n"
                test_message += f'\nПитання: _{question["text"]}_'
                i=1
                for answer in question["options"]:
                    if i==1:
                        question_message = f"\n\n✅ Варіант {i}: *{answer}*"
                    else:
                        question_message = f"\n\n❌ Варіант {i}: *{answer}*"
                    test_message += question_message
                    i+=1
            
            test_message += "\n\n═══════════════════════════════\n"
            await message.answer(text=test_message,parse_mode=ParseMode.MARKDOWN, reply_markup= test_buttons(test_index=tests.index(test)))

    
        
@dispatcher.message(Teacher.questions_count)
async def questions_count_handler(message:Message, state:FSMContext):
    try:
        await state.update_data(questions_count = int(message.text))
        await message.answer("Введіть перше питання:")
        await state.set_state(Teacher.questions_list)
    except:
        await message.answer("Введіть ціле число!")
    await state.update_data(questions_list = [])
    

@dispatcher.message(Teacher.questions_list)
async def questions_list_handler(message:Message, state:FSMContext):
    state_data = await state.get_data()
    questions:list = state_data["questions_list"]
    await state.update_data(options = [])
    await state.set_state(Teacher.options)
    if len(questions) < state_data["questions_count"]:
        await message.answer("Введіть перший варіант відповіді \n *Він завжди буде правильним* ✅", parse_mode=ParseMode.MARKDOWN)
        state_data = await state.get_data()
        questions.append({
            "text": message.text,
            "options": state_data["options"] 
            
        })
        
        await state.update_data(questions_list = questions)
        
        
    else:

        users = read_json("users.json")
        user = users[str(message.from_user.id)]
        user["tests"].append(state_data["questions_list"])
        create_json(data = users, name_file="users.json")
        await message.answer(text="Тест збережено", reply_markup=create_button(["Створити тест", "Переглянути тести"]))
        await state.set_state(Teacher.choice)

    
@dispatcher.message(Teacher.options)
async def options_handler(message:Message, state:FSMContext):
    
    states_data = await state.get_data()
    if message.text != "Перейти до наступного питання":
        
        options_list = states_data["options"]
        options_list.append(message.text)
        await state.update_data(options = options_list)
        await message.answer(
            text="Введiть наступний варiант ❌",
            reply_markup=create_button(["Перейти до наступного питання"])
        )
    
    else:
        await state.set_state(Teacher.questions_list)
        if states_data["questions_count"] > len(states_data["questions_list"]):
            await message.answer("Питання було додано. Введiть наступне питання.")

        else:
            await message.answer(
                text="Ви ввели всi питання. Натиснить на кнопку, щоб зберегти тест.", 
                reply_markup=create_button(["Зберегти тест"])
                )

@dispatcher.message(Student.code)
async def student_code_handler(message:Message, state:FSMContext):
    await state.update_data(code = message.text)
    await message.answer(text="Напишіть своє ім'я")
    await state.set_state(Student.name)

@dispatcher.message(Student.name)
async def student_name_handler(message:Message, state:FSMContext):
    await state.update_data(name = message.text)
    active_tests = read_json("active_tests.json")
    student_data = await state.get_data()
    code = student_data["code"]
    if code in active_tests:
        active_tests[code]["users"].setdefault(str(message.from_user.id), {
            "name": student_data["name"],
            "answers": []
        })
        create_json(data=active_tests, name_file="active_tests.json")
        await message.answer(text="Ви успішно приєдналися до тесту!")
        await state.clear()
    else:
        await message.answer(text="Тест не знайдено. Перевірте код ще раз.")
        