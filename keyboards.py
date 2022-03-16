from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import text, bold
import emoji
from fuzzywuzzy import process


from database import Postgres



# кнопка вызова меню
menu_btn = KeyboardButton('Меню')
call_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(menu_btn)
inline_kb_choose_city = InlineKeyboardMarkup()
inline_kb_choose_city.add(InlineKeyboardButton('Выбрать город', callback_data='btn_choose_city'))

# кнопки меню
def create_inline_kb_menu(user_id, url):
	inline_kb_menu = InlineKeyboardMarkup(row_width=2)
	text_and_data = [
			[emoji.emojize(':green_book: Инструкция', use_aliases=True), 'btn_instruction'],
			[emoji.emojize(':white_check_mark: Выбрать квиз', use_aliases=True), 'btn_choose'],
			[emoji.emojize(':package: Личный кабинет', use_aliases=True), 'btn_lk'],
			]
	row_btns = (InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
	schedule_btn = InlineKeyboardButton(
		emoji.emojize(':date: Посмотреть расписание :date:', use_aliases=True), 
		url=url, callback_data='btn_schedule')
	inline_kb_menu.row(schedule_btn)
	inline_kb_menu.add(*row_btns)
	return inline_kb_menu


back_menu_btn = InlineKeyboardButton('Назад', callback_data='btn_backmenu')
inline_kb_back_menu = InlineKeyboardMarkup()
inline_kb_back_menu.add(back_menu_btn)

# кнопки "личный кабинет"
inline_kb_lk = InlineKeyboardMarkup(row_width=2)
text_and_data = [
		[emoji.emojize(':house_with_garden: Сменить город', use_aliases=True), 'btn_city'],
		[emoji.emojize(':hourglass_flowing_sand: Сменить интервал', use_aliases=True), 'btn_timerange'],
		[emoji.emojize(':busts_in_silhouette: Сменить команду', use_aliases=True), 'btn_team']
]
lk_btns = (InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
inline_kb_lk.add(*lk_btns)
inline_kb_lk.row(back_menu_btn)


# кнопки вкладки "выбрать квиз" под город юзера
def inline_kb_quizes(user_id):
	inline_kb_quizes = InlineKeyboardMarkup(row_width=2)
	db = Postgres()
	names, code_names = db.get_quizes_incity(user_id)
	user_q = [quiz[3] for quiz in db.get_subscriptions(user_id)]
	text_and_data = [[names[i], code_names[i]] for i in range(len(names))]
	row_btns = (InlineKeyboardButton
		(emoji.emojize(f':white_check_mark: {text} :white_check_mark:', use_aliases=True), callback_data='choose_' + data) if text in user_q \
		else InlineKeyboardButton
		(emoji.emojize(f':red_circle: {text} :red_circle:', use_aliases=True), callback_data='choose_' + data) for text, data in text_and_data)
	inline_kb_quizes.add(*row_btns)
	back_menu_btn = InlineKeyboardButton('Назад', callback_data='btn_backmenu')
	inline_kb_quizes.add(back_menu_btn)
	return inline_kb_quizes

#кнопки "сменить интервал"
def inline_kb_timerange(user_id):
	db = Postgres()
	if db.get_user_info(user_id)[0][5] == 'week':
		week_text = emoji.emojize(f':white_check_mark: Неделя :white_check_mark:', use_aliases=True)
		month_text = emoji.emojize(f':red_circle: Месяц :red_circle:', use_aliases=True)
	else:
		week_text = emoji.emojize(f':red_circle: Неделя :red_circle:', use_aliases=True)
		month_text = emoji.emojize(f':white_check_mark: Месяц :white_check_mark:', use_aliases=True)
	week_btn = InlineKeyboardButton(week_text, callback_data='btn_week')
	month_btn = InlineKeyboardButton(month_text, callback_data='btn_month')
	back_lk_btn = InlineKeyboardButton('Назад', callback_data='btn_lk')
	inline_kb_timerange = InlineKeyboardMarkup()
	inline_kb_timerange.add(week_btn, month_btn)
	inline_kb_timerange.row(back_lk_btn)
	return inline_kb_timerange

# проверка стартового квиза
def start_quiz_check(answer):
	correct_answer = ['Бразилиа', 'Brasília', 'Brazilia']
	match_city = process.extractOne(answer.lower(), correct_answer)
	if match_city[1] == 100:
		return True
	else:
		return False



#тексты
welcome_text = text(', привет!',
 			'Ты тоже любишь квизы как и мы?',
			'Тогда ты точно найдешь здесь несколько полезных фишек!',
			'Но для начала необходимо пройти проверку.',
			'Рио-де-Жанейро или Сан-Паулу? Напиши какой город является столицей Бразилии.', sep='\n')
welcome_second_text = text('Нужно было всего-то правильно прочитать вопрос... Добро пожаловать!',
			'А теперь, напиши название своего города.', sep='\n')
error_start_quiz_text = ['Ты серьезно? Попробуй еще раз.', 'Может интеллектуальные игры это не твое?', 'Перечитай вопрос, я специально тебя запутал))).']
error_city_text = text("В этом городе нет квизов или вы ввели название неправильно.",
			'Пожалуйста, введите название без ошибок')
text_menu = text(bold(emoji.emojize('ГЛАВНОЕ МЕНЮ', use_aliases=True)),
			'Отсюда ты можешь управлять функционалом бота.',
			'Открой "Инструкцию" чтобы узнать больше.',
			'Хочешь получить расписание бижайших квизов - просто нажми на кнопку!', sep='\n')

instruction_text = emoji.emojize(text('Привет!:wave: Я могу присылать тебе расписание ближайших квизов!:spiral_calendar_pad:',
			'А еще, я могу автоматически создать голосование в группе твоей команды,',
			'чтобы вы могли определиться на какую игру пойдете. Больше не нужно делать это вручную!:scream_cat:',
			':white_check_mark:Для начала, в меню "Выбрать квиз" добавь свои любимые квизы в избранное.',
			':white_check_mark:Затем, если хочешь, ты можешь изменить временой интервал (по умолчанию я буду присылать квизы на ближайшие 7 дней)',
			':white_check_mark:Если ты просто хочешь получить расписание игр, нажми кнопку "Получить расписание"',
			':white_check_mark:А теперь, самое интересное: добавь меня в группу вашей команды и напиши команду /login',
			'Следующие команды работают только в групповых чатах:',
			'/games - присылает расписание ближайших квизов',
			'/vote - создает голосование из расписания квизов (публичное, с множественным выбором)',
			'Важно: расписание и голосование будет формироваться на основе подписок того пользователя, который ввел команду',
			':fire::fire::fire:Удачи на играх!:fire::fire::fire:', sep='\n'), use_aliases=True)
choose_quiz_text = 'Выбери квиз, расписание которого ты хочешь получать.\nПосле нажатия необходимо подождать 2-3 секунды, пока данные загрузятся.'
change_city_text = text('Хочешь изменить город?',
			'Пришли название нового города.',
			'Для отмены этого действия напиши "Отмена".', sep='\n')
change_timerange_text = 'Выбери временной отрезок за который ты хочешь получать информацию о квизах (на неделю вперед или на месяц вперед)'
login_group_text = text(', ты теперь можешь пользоваться командами бота.',
			'/vote - создать голосование',
			'/games - посмотреть расписание',
			'Количество игр зависит от того, сколько квизов у тебя в избранном', sep='\n')
unav_quizes_text = 'К сожалению, данные квизы, пока не поддерживаются:'

vote_error_text = ', сначала введите команду\n/login'
#'Сначала добавьте квизы в избранное в меню бота, а затем введите команду\n/login в чате'

login_error_text = ', сначала зарегистрируйся в меню бота :)'

change_team_text = text('Хочешь изменить название своей команды?',
			'Пришли новое название.', sep='\n')

