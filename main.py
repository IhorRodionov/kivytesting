from aiogram import types, Bot
import aiogram.utils.markdown as md
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, BotCommand
import pyodbc

server = 'mysqlserver-karazinatimetable.database.windows.net'
database = 'KarazinaTimeTable'
username = 'serveradmin'
password = '{masteroftime-228}'
driver = '{ODBC Driver 17 for SQL Server}'
connection = pyodbc.connect(
    'DRIVER=' + driver + ';SERVER=tcp:' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
TOKEN = '5070843871:AAHZ28tVTeh0QUIYef-3pMNQoMBNqfhVXh0'

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

datatemp = {'lesson': 0,
            'type': 0,
            'tutor': 0,
            'group_num': 0,
            'auditory': 0,
            'date': 0,
            'pare_num': 0}


class Lesson(StatesGroup):
    lesson = State()
    type = State()
    tutor = State()
    group_num = State()
    auditory = State()
    date = State()
    pare_num = State()


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Обновить бота"),
        BotCommand(command="/add", description="Добавить занятие")
    ]
    await bot.set_my_commands(commands)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await set_commands(bot)
    await message.answer("Привет!\nЭто бот для добавления занятий, поэтому работай с ним осторожно ;-)\nДля добавления новой пары пропишите /add")


@dp.message_handler(commands=['add'])
async def process_add_command(message: types.Message):
    await Lesson.lesson.set()
    await bot.send_message(message.chat.id, "Добавим новую пару.\nДля начала напишите название предмета:")


@dp.message_handler(state=Lesson.lesson)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['lesson'] = message.text

    await Lesson.next()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Лекция", "ПЗ")
    markup.add("Консультация")
    markup.add("Семинар", "Факультатив")
    await bot.send_message(message.chat.id, "Укажи тип занятия", reply_markup=markup)


@dp.message_handler(state=Lesson.type)
async def process_type(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['type'] = message.text
        markup = types.ReplyKeyboardRemove()

        await Lesson.next()
        await bot.send_message(message.chat.id, "Введите имя преподавателя:", reply_markup=markup)


@dp.message_handler(state=Lesson.tutor)
async def process_tutor(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['tutor'] = message.text

        await Lesson.next()
        await bot.send_message(message.chat.id, "Введите номер группы:")


@dp.message_handler(lambda message: not message.text.isdigit(), state=Lesson.group_num)
async def process_group_invalid(message: types.Message):
    return await bot.send_message(message.chat.id, "Напишите номер группы числом")


@dp.message_handler(lambda message: message.text.isdigit(), state=Lesson.group_num)
async def process_group(message: types.Message, state: FSMContext):
    await state.update_data(group_num=int(message.text))
    await Lesson.next()
    await bot.send_message(message.chat.id, "Введите аудиторию:")


@dp.message_handler(state=Lesson.auditory)
async def process_auditory(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['auditory'] = message.text

        await Lesson.next()
        await bot.send_message(message.chat.id, "Введите дату:")


@dp.message_handler(state=Lesson.date)
async def process_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['date'] = message.text

        await Lesson.next()
        await bot.send_message(message.chat.id, "Введите номер пары:")


@dp.message_handler(lambda message: not message.text.isdigit(), state=Lesson.pare_num)
async def process_pare_num_invalid(message: types.Message):
    return await bot.send_message(message.chat.id, "Напишите номер пары числом")


@dp.message_handler(lambda message: message.text.isdigit(), state=Lesson.pare_num)
async def process_pare_num(message: types.Message, state: FSMContext):
    await state.update_data(pare_num=int(message.text))

    async with state.proxy() as data:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Отправить", callback_data="send_data"))

        await bot.send_message(
            message.chat.id,
            md.text(
                md.text("Предмет: ", data['lesson']),
                md.text("\nТип: ", data['type']),
                md.text("\nПреподаватель: ", data['tutor']),
                md.text("\nНомер группы: ", data['group_num']),
                md.text("\nАудитория: ", data['auditory']),
                md.text("\nДата: ", data['date']),
                md.text("\nНомер пары: ", data['pare_num'])
            ),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
        datatemp['lesson'] = data['lesson']
        datatemp['type'] = data['type']
        datatemp['tutor'] = data['tutor']
        datatemp['group_num'] = data['group_num']
        datatemp['auditory'] = data['auditory']
        datatemp['date'] = data['date']
        datatemp['pare_num'] = data['pare_num']
    await state.finish()


@dp.callback_query_handler(text="send_data")
async def send_data(call: types.CallbackQuery):
    cursor = connection.cursor()
    cursor.execute("insert into Lessons(lesson,type,tutor,group_num,auditory,date,pare_num) values(?,?,?,?,?,?,?)",
                   datatemp['lesson'],
                   datatemp['type'],
                   datatemp['tutor'],
                   datatemp['group_num'],
                   datatemp['auditory'],
                   datatemp['date'],
                   datatemp['pare_num']
                   )
    cursor.commit()
    await call.message.answer("Отправлено")


@dp.message_handler()
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, "ERROR")


if __name__ == '__main__':
    executor.start_polling(dp)
