from aiogram.utils.markdown import text, hlink
from bs4 import BeautifulSoup
import emoji
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import re
import requests
from telegraph import Telegraph

from database import *

load_dotenv()
TOKEN_TELEGRAPH = os.getenv("TOKEN_TELEGRAPH")

def get_quizes_info(user_id : int): 
    info = []
    for user_quiz in get_user_quizs(user_id):
        quiz = get_quiz(user_id, user_quiz)
        if user_quiz == 'Квиз, плиз!':
            url = f'https://{quiz.city_code}.quizplease.ru/schedule'
            webpage = requests.get(url)
            soup = BeautifulSoup(webpage.text, 'html.parser')
            for column in soup.find_all('div', 'schedule-column'):
                dct = {}
                dct['quiz_name'] = user_quiz
                dct['date'] = column.find('div', re.compile('.+block-date.+')).text.strip().split(', ')[0]
                if len(dct['date'].split(' ')[0]) == 1:
                    dct['date'] = '0' + dct['date']
                dct['time'] = re.compile('\d\d:\d\d').search(str(column.find_all('div'))).group(0)
                dct['game_name'] = column.find('div', re.compile('.+game-card.+')).text.strip('Квиз, плиз!') + ' ' + [a.text for a in column.find_all('div', re.compile('.+game-card'))][1]
                dct['place'] = column.find('div', 'schedule-info-block').find('div', 'techtext').text.strip()
                dct['address'] = column.find('div', 'schedule-info-block').find('div', 'techtext-halfwhite').text.strip()[:-12].strip()
                dct['link'] = url
                info.append(dct)
                #print(dct)
        
        if user_quiz == 'WOW QUIZ':
            if quiz.city_code == 'wowquiz':
                url = (f'https://wowquiz.ru/schedule#')
            else:
                url = (f'https://{quiz.city_code}.wowquiz.ru/schedule#')
            webpage = requests.get(url)
            soup = BeautifulSoup(webpage.text, 'html.parser')
            for column in soup.find_all('div', 'game-column'):
                dct = {}
                dct['quiz_name'] = user_quiz
                dct['date'] = column.find('span', 'date').text
                if len(dct['date'].split(' ')[0]) == 1:
                    dct['date'] = '0' + dct['date']
                dct['time'] = column.find('span', 'time').text
                dct['game_name'] = column.get('data-game_name')
                dct['place'] = column.get('data-place_name')
                dct['link'] = url
                info.append(dct)
                #print(dct)

        if user_quiz == 'Квизиум':
            url = f'https://quizium.ru/ajax?city={quiz.city_code}&date=0&location=all&type=all&status-reserv=0&status=0&category=offline&limit=30&action=get/games'
            headers = {
                    'Accept': '*/*',
                    'Cookie': f'check_city=1; city={quiz.city_code};' + '_fbp=fb.1.1642578903089.4243748; _ym_visorc=w; jivosite_visit=237709; utm_referrer=https://quizium.ru/; utmstat_click_id=72e7b4d0345b8_8528661_5725183; sbjs_current=typ%3Dorganic%7C%7C%7Csrc%3Dgoogle%7C%7C%7Cmdm%3Dorganic%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29; sbjs_session=pgs%3D2%7C%7C%7Ccpg%3Dhttps%3A%2F%2Fquizium.ru%2Fschedule.html; sbjs_udata=vst%3D5%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Macintosh%3B%20Intel%20Mac%20OS%20X%2010_15_7%29%20AppleWebKit%2F605.1.15%20%28KHTML%2C%20like%20Gecko%29%20Version%2F14.1.2%20Safari%2F605.1.15; _ga=GA1.2.1001013549.1642578901; _gid=GA1.2.927698751.1642851611; _ym_isad=2; utmstat_session_start_at=1642944039; sbjs_history={%221%22:{%22src%22:%22google%22%2C%22trm%22:%22(none)%22%2C%22dt%22:%222022-01-19%22}%2C%222%22:{%22src%22:%22google%22%2C%22trm%22:%22(none)%22%2C%22dt%22:%222022-01-19%22}%2C%223%22:{%22src%22:%22google%22%2C%22trm%22:%22(none)%22%2C%22dt%22:%222022-01-19%22}%2C%224%22:{%22src%22:%22google%22%2C%22trm%22:%22(none)%22%2C%22dt%22:%222022-01-19%22}%2C%225%22:{%22src%22:%22google%22%2C%22trm%22:%22(none)%22%2C%22dt%22:%222022-01-19%22}%2C%22count%22:%225%22}; sbjs_current_add=fd%3D2022-01-22%2014%3A40%3A10%7C%7C%7Cep%3Dhttps%3A%2F%2Fquizium.ru%2F%7C%7C%7Crf%3Dhttps%3A%2F%2Fwww.google.com; _gcl_au=1.1.262462487.1642578902; _ym_d=1642578902; _ym_uid=1642578902375215138; utmstat_client_id=1642578902634862156; utmstat_hostname=quizium.ru; sbjs_first=typ%3Dorganic%7C%7C%7Csrc%3Dgoogle%7C%7C%7Cmdm%3Dorganic%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29; sbjs_first_add=fd%3D2022-01-19%2010%3A55%3A01%7C%7C%7Cep%3Dhttps%3A%2F%2Fquizium.ru%2F%7C%7C%7Crf%3Dhttps%3A%2F%2Fwww.google.com; sbjs_migrations=1418474375998%3D1; PHPSESSID=16f2d103b3a3e8253f78117bc6460fd9',
                    'Accept-Language': 'ru',
                    'Host': 'quizium.ru',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
                    'Referer': 'https://quizium.ru/schedule.html',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'X-Requested-With': 'XMLHttpRequest',
                }
            webpage = requests.get(url, headers=headers)
            soup = BeautifulSoup(webpage.text, 'html.parser')
                   
            for column in soup.find_all('div', {'class': ['card-kviz card-kviz-standart',
                                                            'card-kviz card-with-image card-kviz-standart',
                                                            'card-kviz card-with-image card-kviz-standart reserved',
                                                            'card-kviz card-with-image card-kviz-invitation']}):
            
                dct = {}
                dct['quiz_name'] = user_quiz
                date = column.find('span', 'date-kviz').text.lower()
                if len(date.split(' ')[0]) == 1:
                    dct['date'] = '0' + date
                else:
                    dct['date'] = date
                dct['time'] = column.find('span', 'card-time-kviz').text
                dct['game_name'] = column.find('span', 'title-card').text
                dct['place'] = column.find('span', 'card-location-kviz').text
                dct['link'] = 'https://quizium.ru/' + column.find('a', 'link-game').get('href')
                info.append(dct)
                #print(dct)
    #сортировка по дате
    month_translate = {
            'января': '/01',
            'февраля': '/02',
            'марта': '/03',
            'апреля': '/04',
            'мая': '/05',
            'июня': '/06',
            'июля': '/07',
            'августа': '/08',
            'сентября': '/09',
            'октября': '/10',
            'ноября': '/11',
            'декабря': '/12'}
    
    for game in info:
        game['date'] = game['date'].split(', ')[0].split(' ')[0] + \
                            month_translate[game['date'].split(', ')[0].split(' ')[1]] + \
                            '/' + str(datetime.now().year)[-2:]
        
    sorted_date = [date.strftime('%d/%m/%y') for date in sorted(set([datetime.strptime(game['date'], '%d/%m/%y') for game in info]))]
    sorted_info = []
    for date in sorted_date:
        for game in info:
            if game['date'] == date:
                sorted_info.append(game)
    
    # удаляем записи, не соответствующие выбранному отрезку 
    if get_user(user_id=user_id).timerange == 'неделя':
        days = 7
    else:
        days = 30
    for i in range(len(sorted_info)):
        if datetime.strptime(sorted_info[i]['date'], '%d/%m/%y').date() - datetime.now().date() > timedelta(days=days):
            del sorted_info[i:]
            break
    
    return sorted_info


def make_telegraph_schedule(user_id : int):
    data_list = get_quizes_info(user_id)
    telegraph = Telegraph(TOKEN_TELEGRAPH)
    if len(data_list) == 0:
        html_content = '<p>Сначала добавь в избранное хотя бы один квиз</p>'
    else:
        html_content = ''
        for game in data_list:
            html_content += f"<p>:white_check_mark:{game['date']}" + \
                f"<br>:boom:{game['quiz_name']}" + \
                f"<br>:speaker:{game['game_name']}" + \
                f"<br>:round_pushpin:{game['place']}" + \
                f"<br>:clock1:{game['time']}" + \
                f"<br>{hlink('Зарегистрироваться', game['link'])}" + \
                f"<br><br></p>"
    html_content += f"<p>By {hlink('@fuckingcleverbot', 'https://t.me/fuckingcleverbot')}</p>"
    response = telegraph.create_page(
        author_name='Fuckingcleverbot',
        author_url='https://t.me/fuckingcleverbot',
        title='Расписание:', 
        html_content=emoji.emojize(html_content, language='alias'))
    url = 'https://telegra.ph/{}'.format(response['path'])
    return url
    
    
def make_telegraph_rating():
    html_content = ''
    counter = 1
    for user in get_dailyquiz_rating():
        if user['team'] == 'Не указана':
            user['team'] = ' '
        html_content += f"<ol><pre>{counter}.  {user['score']}{user['name']}\n    |{user['team']}</pre></ol>"
        counter += 1
    html_content += f"<p>By {hlink('@fuckingcleverbot', 'https://t.me/fuckingcleverbot')}</p>"
    telegraph = Telegraph(TOKEN_TELEGRAPH)
    response = telegraph.create_page(
        author_name='Fuckingcleverbot',
        author_url='https://t.me/fuckingcleverbot',
        title='Рейтинг:', 
        html_content=emoji.emojize(html_content, language='alias'))
    url = 'https://telegra.ph/{}'.format(response['path'])
    return url
