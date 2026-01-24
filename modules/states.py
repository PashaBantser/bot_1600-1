from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    name = State()
    phone_number = State()
    password = State()

class Teacher(StatesGroup):
    choice = State()
    questions_count = State()
    questions_list = State()
    options = State()

class Student(StatesGroup):
    code = State()
    name = State()
    