from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import emoji
from datetime import datetime, timedelta
import logging
import random

from config import TOKEN
from parser import Parser
import keyboards as kb
from database import Postgres


# задаем уровень логов
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
	user_city = State()
	user_team = State()
	start_quiz = State()

@dp.message_handler(commands=['q'])
async def process_command(message: types.Message):
	await bot.send_message(message.from_user.id, message.from_user.id)

@dp.message_handler(commands=['login'])
async def process_login_command(message: types.Message):
	db = Postgres()
	if not (db.subscriber_exists(message.from_user.id)):
		await bot.send_message(message.chat.id, text=message.from_user.first_name + kb.login_error_text)
	elif message.chat.id == message.from_user.id:
		await bot.send_message(message.from_user.id, 'Эту команду можно использовать только в групповом чате.')
	else:
		db = Postgres()
		db.update_group(message.from_user.id, message.chat.id)
		await bot.send_message(message.chat.id, text=message.from_user.first_name + kb.login_group_text)
	db.add_log(message.from_user.id, datetime.now() + timedelta(hours=3), 'command_login')

@dp.message_handler(commands=['vote'])
async def process_vote_command(message: types.Message):
	db = Postgres()
	if not (db.check_group(message.from_user.id)) and message.chat.id != message.from_user.id:
		await bot.send_message(message.chat.id, text= message.from_user.first_name + kb.vote_error_text)
	elif message.chat.id == message.from_user.id:
		await bot.send_message(message.from_user.id, 'Эту команду можно использовать только в групповом чате.')
	elif db.get_subscriptions(message.from_user.id)[0][3] == 'Null':
		await bot.send_message(message.chat.id, message.from_user.first_name + ', сначала зайдите в меню бота и добавьте в избранное хотябы один квиз.')
	else:
		unav_quizes_list = db.get_unavaliable_quizes(db.get_subscriptions(message.chat.id))
		if (unav_quizes_list):
			unav_quizes = '\n'
			for i in unav_quizes_list:
				unav_quizes += i + '\n'
			await bot.send_message(message.chat.id, text=kb.unav_quizes_text + unav_quizes)

		# создаем опрос
		parser = Parser(message.from_user.id)
		options = parser.make_vote()
		if len(options) <= 10:
			msg = await bot.send_poll(chat_id=message.chat.id, question='Выбираем игру',
									is_anonymous=False, options=options, allows_multiple_answers=True)
		elif len(options) <= 20:
			msg = await bot.send_poll(chat_id=message.chat.id, question='Выбираем игру',
									is_anonymous=False, options=options[:10], allows_multiple_answers=True)
			msg = await bot.send_poll(chat_id=message.chat.id, question='Выбираем игру',
									is_anonymous=False, options=options[10:], allows_multiple_answers=True)
		elif len(options) <= 30:
			msg = await bot.send_poll(chat_id=message.chat.id, question='Выбираем игру',
									is_anonymous=False, options=options[:10], allows_multiple_answers=True)
			msg = await bot.send_poll(chat_id=message.chat.id, question='Выбираем игру',
									is_anonymous=False, options=options[10:20], allows_multiple_answers=True)
			msg = await bot.send_poll(chat_id=message.chat.id, question='Выбираем игру',
									is_anonymous=False, options=options[20:], allows_multiple_answers=True)
		elif len(options) <= 50:
			msg = await bot.send_poll(chat_id=message.chat.id, question='Выбираем игру',
									is_anonymous=False, options=options[:10], allows_multiple_answers=True)
			msg = await bot.send_poll(chat_id=message.chat.id, question='Выбираем игру',
									is_anonymous=False, options=options[10:20], allows_multiple_answers=True)
			msg = await bot.send_poll(chat_id=message.chat.id, question='Выбираем игру',
									is_anonymous=False, options=options[20:30], allows_multiple_answers=True)
			msg = await bot.send_poll(chat_id=message.chat.id, question='Выбираем игру',
									is_anonymous=False, options=options[30:40], allows_multiple_answers=True)
			msg = await bot.send_poll(chat_id=message.chat.id, question='Выбираем игру',
									is_anonymous=False, options=options[40:], allows_multiple_answers=True)
		else:
			await bot.send_message(message.chat.id, text='Похоже, в расписании более 50 квизов. Попробуйте сократить временной интервал или убрать из избранного некоторые квизы.')
	db.add_log(message.from_user.id, datetime.now() + timedelta(hours=3), 'command_vote')

@dp.message_handler(commands=['games'])
async def process_games_command(message: types.Message):
	db = Postgres()	
	if not (db.check_group(message.from_user.id)) and message.chat.id != message.from_user.id:
		await bot.send_message(message.chat.id, text=message.from_user.first_name + kb.vote_error_text)
	elif message.chat.id == message.from_user.id:
		await bot.send_message(message.from_user.id, 'Эту команду можно использовать только в групповом чате.')
	elif db.get_subscriptions(message.from_user.id)[0][3] == 'Null':
		await bot.send_message(message.chat.id, message.from_user.first_name + ', сначала зайдите в меню бота и добавьте в избранное хотябы один квиз.')
	else:
		parser = Parser(message.from_user.id)
		schedule_btn = InlineKeyboardButton(
		emoji.emojize(':date: Посмотреть расписание :date:', use_aliases=True), 
		url=parser.make_telegraph(), callback_data='btn_schedule')
		schedule_kb = InlineKeyboardMarkup().row(schedule_btn)
		await bot.send_message(
			message.chat.id, text=f'Расписание квизов на основе подписок данного пользователя:', 
			reply_markup=schedule_kb, parse_mode=ParseMode.MARKDOWN)
		db.add_log(message.from_user.id, datetime.now() + timedelta(hours=3), 'command_games')


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
	db = Postgres()
	if (not db.subscriber_exists(message.from_user.id)):
		await Form.start_quiz.set()
		await bot.send_message(message.from_user.id, 
				text = message.from_user.first_name + kb.welcome_text)
	else:
		await bot.send_message(message.from_user.id, 
				text = message.from_user.first_name + ', рады снова видеть тебя!\
				\nКнопка вызова меню находится под окном ввода сообщений.',
				reply_markup=kb.call_menu_kb)
	db.add_log(message.from_user.id, datetime.now() + timedelta(hours=3), 'command_start')

# неверный ответ на стартовый вопрос
@dp.message_handler(lambda message: kb.start_quiz_check(str(message.text)) == False, state=Form.start_quiz)
async def process_start_invalid(message: types.Message, state: FSMContext):
	text = random.choice(kb.error_start_quiz_text)
	await message.reply(text=text)

# верный ответ на стартовый вопрос, спрашиваем город
@dp.message_handler(state=Form.start_quiz)
async def process_start_quiz(message: types.Message, state: FSMContext):
	await Form.user_city.set()
	await message.reply(text=kb.welcome_second_text)

# Если город не совпадает
@dp.message_handler(lambda message: Postgres().check_city(str(message.text)) == False, state=Form.user_city)
async def process_num_invalid(message: types.Message, state: FSMContext):
	if message.text.lower() == 'Отмена'.lower():
		await state.finish()
		await bot.send_message(message.from_user.id, text=kb.text_menu, 
			reply_markup=kb.inline_kb_menu, parse_mode=ParseMode.MARKDOWN)
	else:
		await message.reply(text=kb.error_city_text)
	Postgres().add_log(message.from_user.id, datetime.now() + timedelta(hours=3), f'city_incorrect({message.text})')

# получаем город
@dp.message_handler(state=Form.user_city)
async def process_city(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['user_city'] = message.text
		user_city = Postgres().check_city(data['user_city'])
	await state.finish()
	await bot.send_message(message.from_user.id, 
		text = f'Твой город: {user_city}.\nНажми кнопку ниже, чтобы перейти в меню.\nИли пришли сообщение с текстом "Меню"', 
		reply_markup=kb.call_menu_kb, parse_mode=ParseMode.MARKDOWN)
		# добавляем юзера
	db = Postgres()
	if (not db.subscriber_exists(message.from_user.id)):
		db.add_subscriber(
			user_id = message.from_user.id, 
			user_name = message.from_user.username, 
			first_name = message.from_user.first_name, 
			last_name = message.from_user.last_name, 
			city=user_city, 
			first_login = datetime.now())
		db.add_subscription(message.from_user.id, message.from_user.username)
	else:
		db.update_city(message.from_user.id, user_city)
		db.link_update(message.from_user.id, Parser(message.from_user.id).make_telegraph())
	
	db.add_log(message.from_user.id, datetime.now() + timedelta(hours=3), f'set_city{user_city}')

# получаем название команды
@dp.message_handler(state=Form.user_team)
async def process_team(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['user_team'] = message.text
		user_team = data['user_team']
	await state.finish()
	await bot.send_message(message.from_user.id,
			text = f"Твоя команда: «{user_team}».\nНажми кнопку ниже, чтобы перейти в меню.\nИли пришли сообщение с текстом 'Меню'",
			reply_markup=kb.call_menu_kb, parse_mode=ParseMode.MARKDOWN)
	# добавляем команду
	db = Postgres()
	db.update_team(message.from_user.id, user_team)
	
	db.add_log(message.from_user.id, datetime.now() + timedelta(hours=3), f'set_city{user_team}')

# вызов меню
@dp.message_handler()
async def call_menu(message: types.Message):
	if message.text.lower() == 'Меню'.lower():
		db = Postgres()
		if (db.link_exists(message.from_user.id)):
			await bot.send_message(message.from_user.id,
				text=kb.text_menu,
				reply_markup=kb.create_inline_kb_menu(message.from_user.id, db.get_user_info(message.from_user.id)[0][8]),
				parse_mode=ParseMode.MARKDOWN)
		else:
			parser = Parser(message.from_user.id)
			await bot.send_message(message.from_user.id,
				text=kb.text_menu,
				reply_markup=kb.create_inline_kb_menu(
					message.from_user.id, 
					db.link_update(message.from_user.id, parser.make_telegraph())),
					parse_mode=ParseMode.MARKDOWN)

# обработчик кнопок
@dp.callback_query_handler(lambda c: c.data.startswith('btn'))
async def process_callback_button(callback_query: types.CallbackQuery):
	code = callback_query.data
	print(code)
	db = Postgres()
	# меню
	if code == 'btn_schedule':
		db.add_log(callback_query.from_user.id, datetime.now() + timedelta(hours=3), 'btn_schedule')
	
	if code == 'btn_instruction':
		await callback_query.message.edit_text(
			text=kb.instruction_text, reply_markup=kb.inline_kb_back_menu, parse_mode=ParseMode.MARKDOWN)
		db.add_log(callback_query.from_user.id, datetime.now() + timedelta(hours=3), 'btn_instruction')
	
	if code == 'btn_choose':
		await callback_query.message.edit_text(
			text=kb.choose_quiz_text, reply_markup=kb.inline_kb_quizes(callback_query.from_user.id), parse_mode=ParseMode.MARKDOWN)
		db.add_log(callback_query.from_user.id, datetime.now() + timedelta(hours=3), 'btn_choose')
	
	if code == 'btn_city':
		await Form.user_city.set()
		await callback_query.message.edit_text(text=kb.change_city_text)
	
	if code == 'btn_timerange':
		await callback_query.message.edit_text(
			text=kb.change_timerange_text, reply_markup=kb.inline_kb_timerange(callback_query.from_user.id), parse_mode=ParseMode.MARKDOWN)
		db.add_log(callback_query.from_user.id, datetime.now() + timedelta(hours=3), 'btn_timerange')	
	
	if code == 'btn_week':
		db = Postgres()
		db.update_timerange(callback_query.from_user.id, 'week')
		await callback_query.message.edit_text(
			text=kb.change_timerange_text, reply_markup=kb.inline_kb_timerange(callback_query.from_user.id), parse_mode=ParseMode.MARKDOWN)
		db.link_update(callback_query.from_user.id, 
				Parser(callback_query.from_user.id).make_telegraph())
		
	if code == 'btn_month':
		db = Postgres()
		db.update_timerange(callback_query.from_user.id, 'month')
		await callback_query.message.edit_text(
			text=kb.change_timerange_text, reply_markup=kb.inline_kb_timerange(callback_query.from_user.id), parse_mode=ParseMode.MARKDOWN)
		db.update_timerange(callback_query.from_user.id, 'month')
	
	if code == 'btn_team':
		await Form.user_team.set()
		await callback_query.message.edit_text(text=kb.change_team_text)

	if code == 'btn_backmenu':
		await callback_query.message.edit_text(
			text=kb.text_menu, reply_markup=kb.create_inline_kb_menu(callback_query.from_user.id, db.get_user_info(callback_query.from_user.id)[0][8]), parse_mode=ParseMode.MARKDOWN)
	
	if code == 'btn_lk':
		db = Postgres()
		subscriptions = db.get_subscriptions(callback_query.from_user.id)
		user_city = 'Ваш город: \n' + db.get_user_info(callback_query.from_user.id)[0][4]
		user_team = '\n\nВаша команда: \n' + db.get_user_info(callback_query.from_user.id)[0][7]
		user_quizes = '\n\nВаши квизы:'
		for i in subscriptions: user_quizes += '\n' + i[3]
		lk_text = 'ЛИЧНЫЙ КАБИНЕТ\n\n' + user_city + user_team + user_quizes
		await callback_query.message.edit_text(
            text=lk_text, reply_markup=kb.inline_kb_lk, parse_mode=ParseMode.MARKDOWN)
		db.add_log(callback_query.from_user.id, datetime.now() + timedelta(hours=3), 'btn_lk')


	

@dp.callback_query_handler(lambda c: c.data.startswith('choose'))
async def process_callback_choose_button(callback_query: types.CallbackQuery):
	code = callback_query.data
	db = Postgres()
	code_name = code.split('_')[1]
	name = db.switch_codename_name(code_name)[0][0]
	user_quizes = [i[3] for i in db.get_subscriptions(callback_query.from_user.id)]

	# если в БД одна запись с null в графе quiz изменяем эту запись
	if 'Null' in user_quizes and not name in user_quizes:
		db.update_subscription(callback_query.from_user.id, new_quiz=name)
		await callback_query.message.edit_text(
				text=kb.choose_quiz_text, 
				reply_markup=kb.inline_kb_quizes(callback_query.from_user.id), 
				parse_mode=ParseMode.MARKDOWN)
		db.link_update(callback_query.from_user.id, 
					Parser(callback_query.from_user.id).make_telegraph())
	# удаляем запись из бд
	elif name in user_quizes:
		db.delete_subscription(callback_query.from_user.id, name)
		await callback_query.message.edit_text(
				text=kb.choose_quiz_text, 
				reply_markup=kb.inline_kb_quizes(callback_query.from_user.id), 
				parse_mode=ParseMode.MARKDOWN)
		if 'Null' in [i[3] for i in Postgres().get_subscriptions(callback_query.from_user.id)]:
			db.link_update(callback_query.from_user.id, 
					'https://telegra.ph/ERROR-01-26-8')
		else:
			db.link_update(callback_query.from_user.id, 
					Parser(callback_query.from_user.id).make_telegraph())

	# добавляем запись в бд
	else:
		db.add_subscription(callback_query.from_user.id, 
				callback_query.from_user.username, 
				quiz=name)
		await callback_query.message.edit_text(
				text=kb.choose_quiz_text, 
				reply_markup=kb.inline_kb_quizes(callback_query.from_user.id), 
				parse_mode=ParseMode.MARKDOWN)
		db.link_update(callback_query.from_user.id, 
				Parser(callback_query.from_user.id).make_telegraph())

async def scheduled(wait_for):
	while True:
		await asyncio.sleep(wait_for)
		db = Postgres()
		subscribers = db.get_subscribers()
		for s in subscribers:
			url = Parser(s).make_telegraph()
			db.link_update(s, url)



if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.create_task(scheduled(86400)) # каждые n секунд
	executor.start_polling(dp, skip_updates=True)


