import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = Bot(token='7343306090:AAGYlEIBVwE9heIzPr54kWwTBXbVBFKVD3E')
admin_id = '550649516'
dp = Dispatcher()


class Exp(StatesGroup):
    number1 = State()
    operation = State()
    number2 = State()
    sqrt_number = State()
    c = State()


def get_calculator_button():
    markup1 = InlineKeyboardMarkup(inline_keyboard=
                [[InlineKeyboardButton(text="Калькулятор", callback_data="/calc")],
                [InlineKeyboardButton(text="Поддержка", callback_data="/sup")]])
    return markup1


def get_operations_buttons():
    markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="+", callback_data="+"),
                InlineKeyboardButton(text="-", callback_data="-"),
            ],
            [
                InlineKeyboardButton(text="*", callback_data="*"),
                InlineKeyboardButton(text="/", callback_data="/"),
            ],
            [
                InlineKeyboardButton(text="**", callback_data="**"),
                InlineKeyboardButton(text="sqrt", callback_data="sqrt"),
            ],
        ])
    return markup


@dp.message(Command('start'))
async def start(message: Message):
    await message.answer('Выберите действие:', reply_markup=get_calculator_button())


@dp.callback_query(lambda c: c.data == '/calc')
async def calc_callback(callback_query: CallbackQuery, state: FSMContext):
    await cmd_calc(callback_query.message, state)


@dp.callback_query(lambda c: c.data == '/sup')
async def support_callback(callback_query: CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, "Напишите ваше сообщение для обратной связи:")
    await state.set_state(Exp.c)


@dp.message(Exp.c)
async def support(message: Message, state: FSMContext):
    feedback_message = message.text
    await bot.send_message(admin_id, f'Обратная связь от {message.from_user.full_name}: {feedback_message}')
    await message.answer("Ваше сообщение отправлено администратору!")
    await state.clear()
    await message.answer('Выберите оператор: ', reply_markup=get_calculator_button())


@dp.message(Command('calc'))
async def cmd_calc(message: Message, state: FSMContext):
    await state.set_state(Exp.operation)
    await message.answer('Выберите оператор: ', reply_markup=get_operations_buttons())


@dp.callback_query(Exp.operation)
async def process_operation(callback_query: CallbackQuery, state: FSMContext):
    operation = callback_query.data
    await state.update_data(operation=operation)
    if operation == 'sqrt':
        await state.set_state(Exp.sqrt_number)
        await bot.send_message(callback_query.from_user.id, "Введите число для вычисления квадратного корня:")
    else:
        await state.set_state(Exp.number1)
        await bot.send_message(callback_query.from_user.id, "Введите первое число:")


@dp.message(Exp.number1)
async def number_one(message: Message, state: FSMContext):
    try:
        await state.update_data(number1=int(message.text))
        await state.set_state(Exp.number2)
        await message.answer('Введите второе число.')
    except ValueError:
        await message.answer('Введите корректное число.')


@dp.message(Exp.sqrt_number)
async def sqrt_result(message: Message, state: FSMContext):
    try:
        sqrt_number = int(message.text)
        result = sqrt_number ** 0.5
        await message.answer(f'Квадратный корень от {sqrt_number} = {result}')
        await state.clear()
        await message.answer('Выберите действие:', reply_markup=get_calculator_button())
    except ValueError:
        await message.answer('Введите корректное число.')


@dp.message(Exp.number2)
async def get_result(message: Message, state: FSMContext):
    global result, result
    data = await state.get_data()
    first_number = data.get('number1')
    operation = data.get('operation')
    try:
        second_number = int(message.text)
        if operation == '+':
            result = first_number + second_number
        elif operation == '-':
            result = first_number - second_number
        elif operation == '*':
            result = first_number * second_number
        elif operation == '**':
            result = first_number ** second_number
        elif operation == '/':
            if second_number == 0:
                result = "Ошибка: деление на ноль"
            else:
                result = first_number / second_number
        await message.answer(f'{first_number} {operation} {second_number} = {result}')
        await state.clear()
        await message.answer('Выберите действие:', reply_markup=get_calculator_button())
    except ValueError:
        await message.answer('Введите корректное число.')


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
