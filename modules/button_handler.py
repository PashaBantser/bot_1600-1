from .settings import dispatcher
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from .work_json import read_json, create_json
import random
from .buttons import test_button_start, next_question_button, answer_button, end_test_button
from .settings import bot
@dispatcher.callback_query()
async def callback_handler(callback: CallbackQuery):
    await callback.answer(text="button pressed")
    callback_data = callback.data.split("/")
    # callback_data = ["delete_test", 1]
    if callback_data[0] == "delete_test":
        json_data = read_json("users.json")
        
        user: dict = json_data[f"{callback.from_user.id}"]  
        test_list: list = user["tests"]
        test_list.pop(int(callback_data[1]))
        create_json(json_data, "users.json")
        await callback.message.answer(text=f"Тест №{int(callback_data[1]) + 1} було видалено")

        
    elif callback_data[0] == "get_code":
        random_code = random.randint(100000, 999999)
        active_test_data = read_json("active_tests.json")
        json_data = read_json("users.json")
        user: dict = json_data[f"{callback.from_user.id}"]  
        test_list: list = user["tests"]
        test = test_list[int(callback_data[1])]
        test_to_save = {
            "test": test,
            "users": {},
            "owner": f"{callback.from_user.id}"
        }
        active_test_data.setdefault(random_code, test_to_save)
        create_json(active_test_data, "active_tests.json")
        text = f"Код для тесту:\n\n`{random_code}`\n\nНатиснiть на код, щоб скопіювати його"
        await callback.message.answer(
            text=text,
            reply_markup= test_button_start(random_code),
            parse_mode=ParseMode.MARKDOWN
        )
    elif callback_data[0] == "start_test":
        active_test_data = read_json("active_tests.json")
        active_test = active_test_data[callback_data[1]]
        users: dict = active_test["users"]
        test = active_test["test"]
        question = test[0]
        answers_list = []
        for i, answer in enumerate(question["options"]):
            answers_list.append(f"{i+1}) {answer}")
        answers = "\n\n".join(answers_list)
        #answers = "\n\n".join([f"{i+1}) {answer}" for i, answer in enumerate(question["options"])])
        #List comprehension это способ создать список через цикл в одну строчку. джоин соединяет все в одну строку/ в скобках создает список вида 1. answer1 \n 2. answer2 и тд
        for key, _ in users.items():
            await bot.send_message(chat_id = int(key), text = question["text"], reply_markup= answer_button(question["options"], 0, str(callback_data[1])))

        await callback.message.answer(text = question["text"] + "\n\n" + answers, reply_markup= next_question_button(1, str(callback_data[1])))
        
    elif callback_data[0] == "next_question": 
        print(callback_data[2])
        active_test_data = read_json("active_tests.json")
        active_test = active_test_data[callback_data[2]]
        users = active_test["users"]
        test = active_test["test"]

        # if len(test) < 2:
        #     await callback.message.answer(text = "Тест завершено", reply_markup=end_test_button)
        
        question = test[int(callback_data[1])]


        

        
        answers_list = []
        for i, answer in enumerate(question["options"]):
            answers_list.append(f"{i+1}) {answer}")
        answers = "\n\n".join(answers_list)
        #answers = "\n\n".join([f"{i+1}) {answer}" for i, answer in enumerate(test[int(callback_data[1]) + 1]["options"])])

        is_last_question = int(callback_data[1]) == len(test) - 1

        if is_last_question:
            for user_id, user_data in users.items():
                await bot.send_message(chat_id = int(user_id), text = question["text"] + "\n\n_📌 Останнє питання!_", reply_markup= answer_button(question["options"], int(callback_data[1]), str(callback_data[2])))
            await callback.message.answer(text = question["text"] + "\n\n" + answers, reply_markup= end_test_button(str(callback_data[2])))
        else:
            for user_id, user_data in users.items():
                await bot.send_message(chat_id = int(user_id), text = question["text"], reply_markup= answer_button(question["options"], int(callback_data[1]), str(callback_data[2])))
            await callback.message.answer(text = question["text"] + "\n\n" + answers, reply_markup= next_question_button(int(callback_data[1]) + 1, str(callback_data[2])))

        if int(callback_data[1]) + 1 < len(test):
            question = test[int(callback_data[1]) + 1] 
        else:
            pass    
        

    elif callback_data[0] == "answer":
        active_test_data = read_json("active_tests.json")
        active_test = active_test_data[callback_data[2]]
        users: dict = active_test["users"]
        test = active_test["test"]
        
        answer_index = int(callback_data[3])
        question_index = int(callback_data[1])
        question = active_test["test"][question_index]
        
        user = users[str(callback.from_user.id)]
        
        if len(user["answers"]) > question_index:
            text = "Ви вже відповіли на це питання!"
            await callback.answer(text=text)
            await bot.send_message(chat_id=callback.from_user.id, text=text)
            
            return
        
        user["answers"].append(answer_index)
                
        
        create_json(active_test_data, "active_tests.json")
        
        if answer_index == 0:
            result_text = f"✓ Правильна відповідь!"
        else:
            result_text = f"✗ Неправильна відповідь.\n\nПравильна: 1) {question['options'][0]}"
        
        await callback.answer(text=result_text)
        await bot.send_message(chat_id=callback.from_user.id, text=result_text)
        
        if question_index == len(test) - 1:
            await bot.send_message(chat_id=callback.from_user.id, text="_✓ Тест завершено!_", parse_mode=ParseMode.MARKDOWN)

    elif callback_data[0] == "end_test":
        active_test_data = read_json("active_tests.json")
        active_test = active_test_data[callback_data[1]]
        users: dict = active_test["users"]
        test = active_test["test"]
        
        results = []
        for user_id, user_data in users.items():
            user_name = user_data["name"]
            user_answers = user_data["answers"]
            
            correct_count = sum(1 for answer in user_answers if answer == 0)
            total_questions = len(test)
            await bot.send_message(chat_id=int(user_id), text=(
                    "📊 Ваш результат тесту:\n\n" f"Правильних відповідей: {correct_count} з {total_questions}\n"))
            results.append(f"*{user_name}* - _{correct_count}/{total_questions}_")
        

        results_text = "📊 *Результаты теста:*\n\n" + "\n".join(results)
        await callback.message.answer(text=results_text, parse_mode=ParseMode.MARKDOWN)
        active_test_data.pop(callback_data[1])
        create_json(active_test_data, "active_tests.json")
        
      
