from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


def create_button(button_names: list):
    list_buttons = []
    
    for i in range(len(button_names)):
        button = KeyboardButton(text=button_names[i])
        list_buttons.append([button])

    markup = ReplyKeyboardMarkup(keyboard = list_buttons, resize_keyboard=True)
    return markup

def test_buttons(test_index:int):
    button1 = InlineKeyboardButton(text= "Отримати код", callback_data= f"get_code/{test_index}")
    button2 = InlineKeyboardButton(text= "Видалити тест", callback_data= f"delete_test/{test_index}")
    list_buttons = [
        [button1],
        [button2]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=list_buttons)
    return markup 
def test_button_start(test_code:int):
    button1 = InlineKeyboardButton(text= "Розпочати тест", callback_data= f"start_test/{test_code}")
    list_buttons = [
        [button1]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=list_buttons)
    return markup 

def next_question_button(last_question_index:int, code_test:int):
    button1 = InlineKeyboardButton(text= "Наступне питання", callback_data=f"next_question/{last_question_index}/{code_test}")
    list_buttons = [
        [button1]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=list_buttons)
    return markup 



def answer_button(options:list, last_question_index:int, code_test:int):
    list_buttons = []
    
    for i, answer in enumerate(options):
        button = InlineKeyboardButton(text=f"{answer}", callback_data=f"answer/{last_question_index}/{code_test}/{i}")
        list_buttons.append([button])
    
    markup = InlineKeyboardMarkup(inline_keyboard=list_buttons)
    return markup

def end_test_button(code_test:int):
    button1 = InlineKeyboardButton(text= "Завершити тест", callback_data=f"end_test/{code_test}")
    list_buttons = [
        [button1]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=list_buttons)
    return markup
    