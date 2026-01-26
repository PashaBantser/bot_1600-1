from .settings import dispatcher
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from .work_json import read_json, create_json
import random
from .buttons import test_button_start, next_question_button, answer_button, end_test_button
from .settings import bot

@dispatcher.callback_query()
async def callback_handler(callback: CallbackQuery):
    callback_data = callback.data.split("/")
    
    if callback_data[0] == "delete_test":
        json_data = read_json("users.json")
        user: dict = json_data[f"{callback.from_user.id}"]  
        test_list: list = user["tests"]
        test_list.pop(int(callback_data[1]))
        create_json(json_data, "users.json")
        await callback.message.edit_reply_markup(reply_markup=None)
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
        active_test_data.setdefault(str(random_code), test_to_save)
        create_json(active_test_data, "active_tests.json")
        text = f"Код для тесту:\n\n`{random_code}`\n\nНатиснiть на код, щоб скопіювати його"
        await callback.message.answer(
            text=text,
            reply_markup= test_button_start(random_code),
            parse_mode=ParseMode.MARKDOWN
        )
        await callback.answer()

    elif callback_data[0] == "start_test":
        await callback.message.edit_reply_markup(reply_markup=None) 

        active_test_data = read_json("active_tests.json")
        active_test = active_test_data[callback_data[1]]
        users: dict = active_test["users"]
        test = active_test["test"]
        
        question_index = 0
        question = test[question_index]
        
        answers_list = []
        for i, answer in enumerate(question["options"]):
            answers_list.append(f"{i+1}) {answer}")
        answers = "\n\n".join(answers_list)

        for key, _ in users.items():
            try:
                await bot.send_message(
                    chat_id=int(key), 
                    text=question["text"], 
                    reply_markup=answer_button(question["options"], question_index, str(callback_data[1]))
                )
            except:
                pass

        if len(test) == 1:
             await callback.message.answer(
                text=question["text"] + "\n\n" + answers + "\n\n_📌 Це єдине питання!_", 
                reply_markup=end_test_button(str(callback_data[1])),
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await callback.message.answer(
                text=question["text"] + "\n\n" + answers, 
                reply_markup=next_question_button(1, str(callback_data[1]))
            )
        
        await callback.answer()

    elif callback_data[0] == "next_question": 
        await callback.message.edit_reply_markup(reply_markup=None)

        active_test_data = read_json("active_tests.json")
        active_test = active_test_data[callback_data[2]]
        users = active_test["users"]
        test = active_test["test"]

        current_index = int(callback_data[1])
        
        if current_index >= len(test):
             await callback.message.answer("Помилка: Питання закінчились")
             return

        question = test[current_index]

        answers_list = []
        for i, answer in enumerate(question["options"]):
            answers_list.append(f"{i+1}) {answer}")
        answers = "\n\n".join(answers_list)

        is_last_question = current_index == len(test) - 1

        for user_id, user_data in users.items():
            msg_text = question["text"]
            if is_last_question:
                msg_text += "\n\n_📌 Останнє питання!_"
            
            try:
                await bot.send_message(
                    chat_id=int(user_id), 
                    text=msg_text, 
                    reply_markup=answer_button(question["options"], current_index, str(callback_data[2])),
                    parse_mode=ParseMode.MARKDOWN if is_last_question else None
                )
            except:
                pass

        if is_last_question:
            await callback.message.answer(
                text=question["text"] + "\n\n" + answers, 
                reply_markup=end_test_button(str(callback_data[2]))
            )
        else:
            await callback.message.answer(
                text=question["text"] + "\n\n" + answers, 
                reply_markup=next_question_button(current_index + 1, str(callback_data[2]))
            )
        
        await callback.answer()

    elif callback_data[0] == "answer":
        active_test_data = read_json("active_tests.json")
        
        if callback_data[2] not in active_test_data:
            await callback.answer("Цей тест вже завершено")
            return

        active_test = active_test_data[callback_data[2]]
        users: dict = active_test["users"]
        test = active_test["test"]
        
        answer_index = int(callback_data[3])
        question_index = int(callback_data[1])
        question = active_test["test"][question_index]
        
        user_id_str = str(callback.from_user.id)
        if user_id_str not in users:
             await callback.answer("Ви не зареєстровані в цьому тесті")
             return

        user = users[user_id_str]
        
        if len(user["answers"]) > question_index:
            text = "Ви вже відповіли на це питання!"
            await callback.answer(text=text, show_alert=True)
            return
        
        user["answers"].append(answer_index)
        create_json(active_test_data, "active_tests.json")
        
        if answer_index == 0:
            result_text = f"✓ Правильна відповідь!"
        else:
            result_text = f"✗ Неправильна відповідь.\n\nПравильна: 1) {question['options'][0]}"
        
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(text=result_text)
        
        if question_index == len(test) - 1:
            await bot.send_message(chat_id=callback.from_user.id, text="_✓ Тест завершено! Очікуйте результатів від вчителя._", parse_mode=ParseMode.MARKDOWN)
        
        await callback.answer()


    elif callback_data[0] == "end_test":

        await callback.message.edit_reply_markup(reply_markup=None)

        active_test_data = read_json("active_tests.json")
        if callback_data[1] in active_test_data:
            active_test = active_test_data[callback_data[1]]
            users: dict = active_test["users"]
            test = active_test["test"]
            
            results = []
            for user_id, user_data in users.items():
                user_name = user_data["name"]
                user_answers = user_data["answers"]
                
                correct_count = sum(1 for answer in user_answers if answer == 0)
                total_questions = len(test)
                
                try:
                    await bot.send_message(chat_id=int(user_id), text=(
                            "📊 *Ваш результат тесту:*\n\n" 
                            f"Правильних відповідей: {correct_count} з {total_questions}\n"),
                            parse_mode=ParseMode.MARKDOWN
                    )
                except:
                    pass

                results.append(f"*{user_name}* - _{correct_count}/{total_questions}_")
            
            if not results:
                results_text = "📊 *Результати тесту:*\n\nНіхто не пройшов тест"
            else:
                results_text = "📊 *Результати тесту:*\n\n" + "\n".join(results)
            
            await callback.message.answer(text=results_text, parse_mode=ParseMode.MARKDOWN)
            
            active_test_data.pop(callback_data[1])
            create_json(active_test_data, "active_tests.json")
        else:
            await callback.message.answer("Цей тест вже був завершений")
        
        await callback.answer()