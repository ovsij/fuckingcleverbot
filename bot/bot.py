from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
import csv
import emoji
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging
import os
import random

from .keyboards import *
from database import *


# задаем уровень логов
logging.basicConfig(level=logging.INFO)

# инициализируем бота
load_dotenv()
bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher(bot, storage=MemoryStorage())

class Form(StatesGroup):
    user_city = State()
    user_team = State()
    new_message = State()
    
    
@dp.message_handler(commands=['start', 'menu'])
async def process_start_command(message: types.Message):
    # если юзера нет в базе, спрашиваем город
    if (not exists_user(message.from_user.id)):
        await Form.user_city.set()
        text = inline_kb_welcome_false(message.from_user.first_name)
        await bot.send_message(
            message.from_user.id, 
			text = text)
    # если юзер в базе, вызываем меню
    else:
        text, reply_markup = inline_kb_menu(message.from_user.id)
        await bot.send_message(
            message.from_user.id, 
			text=text,
			reply_markup=reply_markup)

# если города нет в базе
@dp.message_handler(lambda message: city_exists(city=message.text) == False, state=Form.user_city)
async def process_num_invalid(message: types.Message, state: FSMContext):
    await bot.send_message(
            message.from_user.id, 
			text=text(
                'Упс, у нас пока нет данных о квизах в этом городе или вы ввели его неправильно.',
                'Введите название правильно или введите другой город (вам будет доступна викторина).', sep='\n'))

# получаем город и добавляем юзера в базу
@dp.message_handler(state=Form.user_city)
async def form_user_city(message: types.Message, state: FSMContext):
    await state.finish()
    if (not exists_user(message.from_user.id)):
        create_user(user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            city=city_exists(city=message.text))
        update_user(user_id=message.from_user.id,
            quizs='quizplease'
            )
        text, reply_markup = inline_kb_menu(message.from_user.id)
        await bot.send_message(
            message.from_user.id, 
            text=text,
            reply_markup=reply_markup)
    else:
        update_user(user_id=message.from_user.id,
            city=city_exists(city=message.text),
            )
        text, reply_markup = inline_kb_settings(message.from_user.id)
        await bot.send_message(
            message.from_user.id, 
            text=text,
            reply_markup=reply_markup)


# получаем название команды
@dp.message_handler(state=Form.user_team)
async def process_team(message: types.Message, state: FSMContext):
    await state.finish()
    update_user(user_id=message.from_user.id, team=message.text)
    text, reply_markup = inline_kb_settings(message.from_user.id)
    await bot.send_message(
        message.from_user.id, 
        text=text,
        reply_markup=reply_markup)


# обработчик кнопок
@dp.callback_query_handler(lambda c: c.data.startswith('btn'))
async def btn_backmenu_denyadd(callback_query: types.CallbackQuery):
    code = callback_query.data
    print(code)
    # назад в меню
    if code == 'btn_backmenu':
        text, reply_markup = inline_kb_menu(callback_query.from_user.id)
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup)
    # /загрузить расписание 
    if code == 'btn_schedule':
        text, reply_markup = inline_kb_menu(callback_query.from_user.id, schedule=True)
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup)
    # /выбор квиза
    if code == 'btn_choose':
        text, reply_markup = inline_kb_choose(callback_query.from_user.id)
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup)
    # /выбор квиза / подписка и отписка на квиз
    if any(True if code.split('_')[1] == quiz[1] else False for quiz in get_city_quizs(callback_query.from_user.id)):
        if code.split('_')[-1] == 'del':
            del_quiz = True
        else:
            del_quiz = False
        update_user(user_id=callback_query.from_user.id, quizs=code.split('_')[1], del_quiz=del_quiz)
        text, reply_markup = inline_kb_choose(callback_query.from_user.id)
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup)
    # /настройки
    if code == 'btn_settings':
        text, reply_markup = inline_kb_settings(callback_query.from_user.id)
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup)
    # /настройки/ изменить город
    if code == 'btn_city':
        await Form.user_city.set()
        await callback_query.message.edit_text(text='Введите название города:')
    # /настройки/ изменить команду
    if code == 'btn_team':
        await Form.user_team.set()
        await callback_query.message.edit_text(text='Введите название команды:')
    # /настройки/ изменить интервал
    if code == 'btn_timerange':
        text, reply_markup = inline_kb_timerange(callback_query.from_user.id)
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup)
    # /настройки/ изменить интервал / интервал = неделя
    if code == 'btn_week':
        update_user(user_id=callback_query.from_user.id, timerange='неделя')
        text, reply_markup = inline_kb_timerange(callback_query.from_user.id)
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup)
    # /настройки/ изменить интервал / интервал = месяц
    if code == 'btn_month':
        update_user(user_id=callback_query.from_user.id, timerange='месяц')
        text, reply_markup = inline_kb_timerange(callback_query.from_user.id)
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup)
    # /викторина
    if code == 'btn_quiz':
        text, reply_markup = inline_kb_quiz(callback_query.from_user.id)
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN)
    # /викторина/начать
    if code == 'btn_daily_start':
        update_dailyquiz(user_id=callback_query.from_user.id, daily_score=0, fifty=True, mistake=True, last_game=datetime.now())
        text, reply_markup = btn_daily_question(callback_query.from_user.id)
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN)
    # /викторина/начать/правильный ответ
    if code.split('_')[1] == 'correct':
        if code.split('_')[2] == 'nz':
            text, reply_markup = btn_daily_question(callback_query.from_user.id, counter=int(code.split('_')[-1]), correct=True, nz=True)
        else:
            update_dailyquiz(user_id=callback_query.from_user.id, daily_score=1, score=1)
            text, reply_markup = btn_daily_question(callback_query.from_user.id, counter=int(code.split('_')[-1]), correct=True)
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN)
    # /викторина/начать/неправильный ответ
    if code.split('_')[1] == 'uncorrect':
        if code.split('_')[2] == 'nz':
            text, reply_markup = btn_daily_question(callback_query.from_user.id, counter=int(code.split('_')[-1]), correct=False, mistake=False, nz=True)
        else:
            mistake = get_dailyquiz(user_id=callback_query.from_user.id).mistake
            text, reply_markup = btn_daily_question(callback_query.from_user.id, counter=int(code.split('_')[-1]), correct=False, mistake=mistake)
            update_dailyquiz(user_id=callback_query.from_user.id, mistake=False)
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN)
    # /викторина/начать/50_на_50
    if code.split('_')[1] == 'fifty':
        update_dailyquiz(user_id=callback_query.from_user.id, fifty=False)
        text, reply_markup = btn_daily_question(callback_query.from_user.id, counter=int(code.split('_')[-1]), correct=True, fifty=True)
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN)
    


# отправить сообщение всем юзерам
@dp.message_handler(lambda message: message.from_user.id == int(os.getenv('admin_id')) and message.text == "Сообщение")
async def process_callback_button(message: types.Message):
    text = 'Введите текст сообщения'
    await Form.new_message.set()
    await bot.send_message(
            message.from_user.id,
            text=text, 
            parse_mode=ParseMode.MARKDOWN
            )

# получаем текст сообщения для рассылки
@dp.message_handler(state=Form.new_message)
async def process_city(message: types.Message, state: FSMContext):
    await state.finish()
    text = message.text
    reply_markup = inline_sendmessage()
    await bot.send_message(
            message.from_user.id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
            )

# Рассылка сообщения
@dp.callback_query_handler(lambda c: c.data == 'aceptsending')
async def process_callback_button(callback_query: types.CallbackQuery):
    
    for user_id in get_users():
        try:
            await bot.send_message(
                user_id,
                text=callback_query.message.text
            )
        except:
            continue
    
    await bot.send_message(
            callback_query.from_user.id,
            text='Сообщение отправлено пользователям.'
            )

# Отмена рассылки сообщения
@dp.callback_query_handler(lambda c: c.data == 'denysending')
async def process_callback_button(callback_query: types.CallbackQuery):
    await bot.send_message(
            callback_query.from_user.id,
            text='Сообщение не разослано.')
