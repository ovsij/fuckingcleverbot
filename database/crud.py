from bs4 import BeautifulSoup
import csv
from fuzzywuzzy import process
import requests

from .db import *


@db_session()
def create_user(
    user_id : int, 
    username : str,
    first_name : str,
    last_name : str,
    city : str
    ):

    if not User.exists(user_id=user_id):
        user = User(user_id=user_id, username=username, first_name=first_name, last_name=last_name, city=city)
        Daily_quiz(user=user)
        flush()
        return user
    else:
        print(f'User {user_id} exists')


@db_session()
def update_user(
    user_id : int, 
    username : str = None,
    first_name : str = None,
    last_name : str = None,
    city : str = None,
    timerange : str = None,
    team : str = None,
    group_id : int = None,
    quizs = None,
    del_quiz : bool = False #если нужно удалить подписку на указанный квиз, ставим True
    ):

    user_to_update = User.get(user_id = user_id)
    if username:
        user_to_update.username = username
    if first_name:
        user_to_update.first_name = first_name
    if last_name:
        user_to_update.last_name = last_name
    if city:
        # сначала проверяем есть ли квизы в этом городе
        if Quiz.exists(city=city):
            user_to_update.city = city
            # при смене города обновляем квизы
            new_quizs = []
            for quiz in user_to_update.quizs:
                if Quiz.exists(name=quiz.name, city=city): # если в новом городе нет какого-то квиза связь удаляется
                    new_quizs.append(Quiz.get(name=quiz.name, city=city))
            user_to_update.quizs = new_quizs
            return city
        else:
            return 'Недоступен'
    if timerange:
        user_to_update.timerange = timerange
    if team:
        user_to_update.team = team
    if group_id:
        user_to_update.group_id = group_id
    if quizs:
        if not del_quiz:
            user_to_update.quizs += Quiz.get(codename=quizs, city=user_to_update.city)
        else:
            user_to_update.quizs -= Quiz.get(codename=quizs, city=user_to_update.city)


@db_session()
def get_user(user_id : int):
    return User.get(user_id=user_id)

@db_session()
def get_users():
    return [int(user.user_id) for user in User.select_by_sql('SELECT id, user_id FROM User')[:]]

@db_session()
def get_quiz(user_id : int, name : str):
    user = User.get(user_id=user_id)
    return Quiz.get(name=name, city=user.city)

@db_session()
def get_city_quizs(user_id : int):
    city = User.get(user_id=user_id).city
    quizs = []
    for quiz in Quiz.select(city=city):
        quizs.append([quiz.name, quiz.codename])
    return quizs

@db_session()
def get_user_quizs(user_id : int): 
    quizs = []
    for quiz in User.get(user_id=user_id).quizs:
        if quizs not in quizs:
            quizs.append(quiz.name)
    # -> список name на которые подписан юзер
    return quizs

@db_session()
def exists_user(user_id : int):
    return User.exists(user_id=user_id)

@db_session()
def city_exists(city : str):
    # может я что не понял в pony, но вывести уникальные города удалось только так
    cities = []
    for quiz in Quiz.select()[:]:
        if quiz.city not in cities:
            cities.append(quiz.city)
    match_city = process.extractOne(city.lower(), cities)
    if match_city[1] > 60 and len(city) - len(match_city[0]) <= 3 and city[0].lower() == match_city[0][0].lower():
        return match_city[0]
    else:
        return False

@db_session
def update_dailyquiz(
    user_id : int,
    score : int = 0,
    daily_score : int = 2,
    fifty : bool = 2,
    mistake : bool = 2,
    last_game : datetime = 0
    ):
    dq_to_update = Daily_quiz.get(user = get_user(user_id=user_id))
    if score:
        dq_to_update.score += score
    if daily_score == 0:
        dq_to_update.daily_score = daily_score
    if daily_score == 1:
        dq_to_update.daily_score += daily_score
    if fifty == True:
        dq_to_update.fifty = fifty
    if fifty == False:
        dq_to_update.fifty = fifty
    if mistake == True:
        dq_to_update.mistake = mistake
    if mistake == False:
        dq_to_update.mistake = mistake
    if last_game:
        dq_to_update.last_game = last_game

@db_session
def get_dailyquiz(user_id : int):
    user = User.get(user_id=user_id)
    return Daily_quiz.get(user=user)

@db_session
def get_dailyquiz_rating():
    quiz = Daily_quiz.select_by_sql("SELECT * FROM Daily_quiz ORDER BY score DESC, last_game ASC")
    rating = []
    for q in quiz:
        user = User.get(id=q.user.id)
        
        last_name = [last_name for last_name in [user.last_name, ' '] if last_name][0]
        name = user.first_name + ' ' + last_name
        if len(name) < 20:
            name += ' ' * (20 - len(name))

        score = f'|   {q.score}   |'
        if len(score) < 10:
            score += ' ' * (10 - len(score))
        
        rating.append({'name': name, 'team': user.team, 'score': score, 'daily_score': q.daily_score})
    return rating


@db_session
def create_quiz():
    # квизплиз
    url = 'https://quizplease.ru'
    webpage = requests.get(url)
    soup = BeautifulSoup(webpage.text, 'html.parser')

    divs = soup.find('div', 'city-droplist-column').find_all('a', 'city-droplink w-dropdown-link')
    quizpleaze = [{'name': 'Квиз, плиз!', 
                    'codename': 'quizplease', 
                    'city': div.text, 
                    'city_code': div.get('href').split('.')[0].split('/')[-1]} for div in divs]

    # wow quiz
    url = 'https://wowquiz.ru/schedule#'
    webpage = requests.get(url)
    soup = BeautifulSoup(webpage.text, 'html.parser')
    wowquiz = [{'name': 'WOW QUIZ', 
                'codename': 'wowquiz', 
                'city': div.text, 
                'city_code': div.find('span').get('data-href').split('//')[1].split('.')[0]} for div in soup.find_all('div', 'header__nav-location')]

    # квизиум
    url = 'https://quizium.ru/schedule.html'
    webpage = requests.get(url)
    soup = BeautifulSoup(webpage.text, 'html.parser')

    divs = soup.find('div', 'wrapper').find_all('li')
    quizium = [{'name': 'Квизиум', 
                    'codename': 'quizium', 
                    'city': div.text, 
                    'city_code': div.get('data-city')} for div in divs]
    
    for quiz in quizpleaze + wowquiz + quizium:
        if not Quiz.get(
            name=quiz['name'], 
            city=quiz['city'],
            ): # исключает повторную запись квиза

            Quiz(
            name=quiz['name'], 
            codename=quiz['codename'],
            city=quiz['city'],
            city_code=quiz['city_code']
            )
            
    # наполняю своими юзерами из старой базы
    with open('database/local/users.csv', 'r', newline='') as csvfile:
        file = csv.reader(csvfile, delimiter=',')
        for row in file:
            User(
                user_id = row[1],
                username = row[2],
                first_name = row[3],
                last_name = row[4],
                city = row[5],
                timerange = row[6],
                team = row[7],
                group_id = None,
                first_login = row[9],
            )

