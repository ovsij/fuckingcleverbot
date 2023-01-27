from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import text, bold
from emoji import emojize
from datetime import datetime
import random

from database import *
from parser import *

# клавиатура с возвратом в меню
back_menu_btn = InlineKeyboardButton(emojize(':arrow_left: Назад :arrow_left:', language='alias'), callback_data='btn_backmenu')
inline_kb_back_menu = InlineKeyboardMarkup()
inline_kb_back_menu.add(back_menu_btn)

# приветствие для нового пользователя
def inline_kb_welcome_false(first_name):
    txt = text(
        first_name + emojize(', привет :wave:', language='alias'),
        emojize('Чтобы начать пользоваться ботом пришли мне свой город :arrow_down:', language='alias'),
        sep='\n'
    )
    return txt

# меню
def inline_kb_menu(user_id : int, schedule : bool = False):
    user = get_user(user_id)
    last_name = [last_name for last_name in [user.last_name, ' '] if last_name][0] # исключаем None
    quizs = get_user_quizs(user_id)
    txt = 'ГЛАВНОЕ МЕНЮ'
    txt += text('\n',
        f'Игрок: {user.first_name} {last_name}',
        f'Город: {user.city}',
		f'Команда: {user.team}',
		f'Интервал расписания: {user.timerange}',
        ' ',
		f'Ваши подписки:', 
        sep='\n')
    for quiz in quizs:
        txt += f'\n {quiz}'
    txt += f'\n\nОбщий счет: {get_dailyquiz(user_id).score}'
    if get_dailyquiz(user_id).last_game.date() == datetime.now().date():
        txt += f'\nСегодня: {get_dailyquiz(user_id).daily_score}'
    else:
        txt += f'\nСегодня: 0'

    text_and_data = [
        [emojize(':date: Загрузить расписание :date:', language='alias'), 'btn_schedule'],
		[emojize(':white_check_mark: Выбрать квиз :white_check_mark:', language='alias'), 'btn_choose'],
		[emojize(':gear: Настройки :gear:', language='alias'), 'btn_settings'],
        [emojize(':collision: Ежедневная викторина :collision:', language='alias'), 'btn_quiz']
		]
    inline_kb = InlineKeyboardMarkup(row_width=1)
    if schedule:
        del text_and_data[0]
        url = make_telegraph_schedule(user_id=user_id)
        inline_kb.add(InlineKeyboardButton(emojize(':date: Открыть расписание :date:', language='alias'), url=url))
    row_btns = (InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
    inline_kb.add(*row_btns)
    return txt, inline_kb

# выбор квиза
def inline_kb_choose(user_id):
    text = 'ВЫБРАТЬ КВИЗ'
    txt, i = inline_kb_menu(user_id)
    text += txt[12:]

    quizs = get_city_quizs(user_id)
    user_quizs = get_user_quizs(user_id)
    text_and_data = [(emojize(f':white_check_mark: {quiz[0]}', language='alias'), f'btn_{quiz[1]}_del') if quiz[0] in user_quizs else (quiz[0], f'btn_{quiz[1]}') for quiz in quizs]
    inline_kb = InlineKeyboardMarkup(row_width=1)
    row_btns = (InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
    inline_kb.add(*row_btns)
    inline_kb.add(back_menu_btn)
    return text, inline_kb

# настройки
def inline_kb_settings(user_id : int):
    text = 'НАСТРОЙКИ'
    txt, i = inline_kb_menu(user_id)
    text += txt[12:]

    inline_kb = InlineKeyboardMarkup(row_width=1)
    text_and_data = [
		['Изменить город', 'btn_city'],
		['Изменить команду', 'btn_team'],
        ['Изменить интервал', 'btn_timerange'],
		]
    row_btns = (InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
    inline_kb.add(*row_btns)
    inline_kb.row(back_menu_btn)
    return text, inline_kb

# изменить интервал
def inline_kb_timerange(user_id):
    text = 'НАСТРОЙКИ'
    txt, i = inline_kb_menu(user_id)
    text += txt[12:]

    timerange = get_user(user_id).timerange
    if timerange == 'неделя':
        text_and_data = [
		    [emojize(':white_check_mark: Неделя :white_check_mark:', language='alias'), 'btn_week'],
		    [emojize(':red_circle: Месяц :red_circle:', language='alias'), 'btn_month'],
		]
    else:
        text_and_data = [
		    [emojize(':red_circle: Неделя :red_circle:', language='alias'), 'btn_week'],
		    [emojize(':white_check_mark: Месяц :white_check_mark:', language='alias'), 'btn_month'],
		]
    inline_kb = InlineKeyboardMarkup(row_width=1)
    row_btns = (InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
    back_settings_btn = InlineKeyboardButton(emojize(':arrow_left: Назад :arrow_left:', language='alias'), callback_data='btn_settings')
    inline_kb.add(*row_btns)
    inline_kb.row(back_settings_btn)
    return text, inline_kb

# /викторина
def inline_kb_quiz(user_id : int):
    text = 'ЕЖЕДНЕВНАЯ ВИКТОРИНА'
    txt, i = inline_kb_menu(user_id)
    text += txt[12:]
    
    inline_kb = InlineKeyboardMarkup(row_width=1)
    telegraph = make_telegraph_rating()
    if not (get_dailyquiz(user_id=user_id).last_game.date() == datetime.now().date()):
        inline_kb.add(InlineKeyboardButton(emojize(':sparkle: Начать :sparkle:', language='alias'), callback_data='btn_daily_start'))
        inline_kb.add(InlineKeyboardButton(emojize(':reminder_ribbon: Рейтинг игроков :reminder_ribbon:', language='alias'), url=telegraph))
    else:
        inline_kb.add(InlineKeyboardButton(emojize(':anger: Вы уже сегодня играли :anger:', language='alias'), callback_data='btn_daily_error'))
        inline_kb.add(InlineKeyboardButton(emojize(':reminder_ribbon: Рейтинг игроков :reminder_ribbon:', language='alias'), url=telegraph))
    inline_kb.row(back_menu_btn)
    return text, inline_kb



def btn_daily_question(
    user_id : int, 
    counter : int = 1, 
    correct: bool = False, 
    mistake : bool = True,
    fifty : bool = False,
    nz : bool = False):

    questions = []
    with open(f"./dailyquiz/{datetime.now().strftime('%m-%d-%Y')}.csv", 'r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            questions.append(row)
    text = ''
    if correct and not fifty:
        text = 'Верно!'
    elif not correct and mistake == False and counter > 1:
        text = f'Не верно :(\nПравильный ответ: {questions[counter-1][2]}'
    elif not correct and mistake == True and counter > 1:
        text = f'Не верно :(\nНо один раз ошибиться мажно!\nПравильный ответ:{questions[counter-1][2]}'
    
    if nz:
        text += f'\n\nВы набрали: {get_dailyquiz(user_id=user_id).daily_score} балла\nДальше игра вне зачета'

    

    if get_dailyquiz(user_id=user_id).mistake and counter !=11 or counter == 1 and not fifty:
        text += f'\n\n{questions[counter][1]}'
        text_and_data = [
                [questions[counter][2], 'btn_correct_' + str(counter + 1)],
                [questions[counter][3], 'btn_uncorrect_' + str(counter + 1)],
                [questions[counter][4], 'btn_uncorrect_' + str(counter + 1)],
                [questions[counter][5], 'btn_uncorrect_' + str(counter + 1)]
            ]
        random.shuffle(text_and_data)
        inline_kb = InlineKeyboardMarkup(row_width=2)
        row_btns = (InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
        inline_kb.add(*row_btns)
    elif counter == 11:
        text += f'\n\nВы набрали: {get_dailyquiz(user_id=user_id).daily_score} баллов'
        inline_kb = InlineKeyboardMarkup(row_width=2)
        back_btn = InlineKeyboardButton(emojize(':arrow_left: Назад :arrow_left:', language='alias'), callback_data='btn_quiz')
        inline_kb.add(back_btn)
    else:
        text += f'\n\n{questions[counter][1]}'
        text_and_data = [
                [questions[counter][2], 'btn_correct_nz_' + str(counter + 1)],
                [questions[counter][3], 'btn_uncorrect_nz_' + str(counter + 1)],
                [questions[counter][4], 'btn_uncorrect_nz_' + str(counter + 1)],
                [questions[counter][5], 'btn_uncorrect_nz_' + str(counter + 1)]
            ]
        random.shuffle(text_and_data)
        inline_kb = InlineKeyboardMarkup(row_width=2)
        row_btns = (InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
        inline_kb.add(*row_btns)
    
    if fifty:
        text_and_data = [
                [questions[counter][2], 'btn_correct_' + str(counter + 1)],
                [questions[counter][3], 'btn_uncorrect_' + str(counter + 1)],
                [questions[counter][4], 'btn_uncorrect_' + str(counter + 1)],
                [questions[counter][5], 'btn_uncorrect_' + str(counter + 1)]
            ]
        # удаляем 2 неверных ответа
        delete = []
        while len(delete) < 2:
            random_int = random.randint(1,3)
            if random_int not in delete:
                delete.append(random_int)

        del text_and_data[max(delete)]
        del text_and_data[min(delete)]

        random.shuffle(text_and_data)
        inline_kb = InlineKeyboardMarkup(row_width=2)
        row_btns = (InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
        inline_kb.add(*row_btns)
    
    if (get_dailyquiz(user_id).fifty) and counter != 11:
        fifty_fifty_btn = InlineKeyboardButton('Подсказка: 50 на 50', callback_data= 'btn_fifty_' + str(int(counter)))
        inline_kb.row(fifty_fifty_btn)
    return text, inline_kb


# проверка сообщения перед отправкой
def inline_sendmessage():
	inline_kb_sendmessage = InlineKeyboardMarkup(row_width=1)
	btn_send = InlineKeyboardButton(emoji.emojize(':white_check_mark: Отправить :white_check_mark:', language='alias'), callback_data = 'aceptsending')
	btn_deny = InlineKeyboardButton(emoji.emojize(':x: Отменить :x:', language='alias'), callback_data = 'denysending')
	inline_kb_sendmessage.row(btn_send)
	inline_kb_sendmessage.row(btn_deny)
	return inline_kb_sendmessage