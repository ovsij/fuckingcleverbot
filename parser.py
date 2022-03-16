from aiogram.utils.markdown import text, hlink
import requests
from bs4 import BeautifulSoup
import re
import emoji
from database import Postgres
from datetime import datetime, timedelta
from telegraph import Telegraph

from config import TOKEN_TELEGRAPH
from month_translate import month_translate

class Parser:
    def __init__(self, user_id):
        self.db = Postgres()
        self.user_id = user_id
        self.user_info = self.db.get_user_info(user_id)
        self.quizes_incity, c = self.db.get_quizes_incity(user_id)
        self.quiz_list = [quiz[3] for quiz in self.db.get_subscriptions(user_id)]   
        self.timerange = self.db.get_user_info(user_id)[0][5]
        print('Scraping - running')
    
    def check_date(self, date):
        try:
            # сокращаем подборку, если срок неделя
            datetime_string = date.split(', ')[0].split(' ')[0] + \
                    month_translate[date.split(', ')[0].split(' ')[1]] + \
                    '/' + str(datetime.now().year)[-2:]
                                    
            date_obj = datetime.strptime(datetime_string, '%d/%m/%y')
            delta = date_obj - datetime.now()
            if delta < timedelta(days=7):
                return True
            elif delta > timedelta(days=7) and self.timerange == 'month':
                return True
            elif delta > timedelta(days=7) and self.timerange == 'week':
                return False
        except:
            return False

    def get_info(self):
        info = []
        for quiz in self.quiz_list:
            if quiz == 'Квиз, плиз!' and quiz in self.quizes_incity:
                city_code = self.db.switch_city_name_codename(self.user_info[0][4], quiz)
                url = f'https://{city_code}.quizplease.ru/schedule'
                webpage = requests.get(url)
                soup = BeautifulSoup(webpage.text, 'html.parser')
                for column in soup.find_all('div', 'schedule-column'):
                    dct = {}
                    dct['quiz'] = 'Квиз, Плиз!'
                    date = column.find(True, {'class': ['h3 h3-green h3-mb10', 
                                                                'h3 h3-pink h3-mb10', 
                                                                'h3 h3-yellow h3-mb10']}).text.split(', ')[0]
                    if len(date.split(' ')[0]) == 1:
                        dct['date'] = '0' + date
                    else:
                        dct['date'] = date
                    for block in column.find_all('div', 'schedule-info'):
                        if re.search(r'\d\d.\d\d', block.text.strip('\n')):
                            dct['time'] = block.text.strip('\n')
                    dct['name'] = column.find('div', 'h2 h2-game-card h2-left').text + column.find('div', 'h2 h2-game-card').text
                    dct['place'] = column.find('div', 'schedule-block-info-bar').text\
                                        .strip('\t').strip(' ')\
                                        .rstrip('\tИнфа о баре\n')
                    buttons = column.find('div', {'class': ['game-buttons available',
                                                        'game-buttons available w-clearfix']}).find_all('a')
                    if len(buttons) > 1:
                        dct['reg'] = f'https://{city_code}.quizplease.ru' + buttons[1].get('href')
                    else:
                        dct['reg'] = f'https://{city_code}.quizplease.ru' + buttons[0].get('href')
                    
                    if (self.check_date(dct['date'])):
                        info.append(dct)
                    else:
                        break

                    

            if quiz == 'Смузи' and quiz in self.quizes_incity:
                url = self.db.switch_city_name_codename(self.user_info[0][4], quiz)
                webpage = requests.get(url)
                soup = BeautifulSoup(webpage.text, 'html.parser')
                columns = soup.find_all('div', "freebirdFormviewerComponentsQuestionRadioChoice freebirdFormviewerComponentsQuestionRadioOptionContainer freebirdFormviewerComponentsQuestionRadioImageChoiceContainer")
                for column in columns:
                    dct = {}
                    game_data = column.find('span', 'docssharedWizToggleLabeledLabelText exportLabel freebirdFormviewerComponentsQuestionRadioLabel').text
                    dct['quiz'] = 'Смузи'
                    date = ' '.join(game_data.split(' ')[:2])
                    if len(date.split(' ')[0]) == 1:
                        dct['date'] = '0' + date
                    else:
                        dct['date'] = date
                    dct['time'] = game_data.split(' ')[3].strip(',').strip('- ')
                    dct['place'] = ' '.join(game_data.split(' ')[4:6]).strip('(').strip(')').strip('.').split('.')[0].split(')')[0]
                    try:  
                        with_descr = game_data.split(dct['place'])[1].split('№')
                        name = with_descr[0].strip(') ').strip('. ') + ' №' + with_descr[1][:2]
                        if len(name) > 40:
                            dct['name'] = game_data.split(dct['place'])[1][:40].strip(') ')
                        else:
                            dct['name'] = name
                    except:
                        dct['name'] = 'ERROR - Уточните название, нажав "Зарегистрироваться"'
                    dct['reg'] = url
                    if (self.check_date(dct['date'])):
                        info.append(dct)
                    else:
                        break

            if quiz == 'Квизиум' and quiz in self.quizes_incity:
                city_code = self.db.switch_city_name_codename(self.user_info[0][4], quiz)
                url = f'https://quizium.ru/ajax?city={city_code}&date=0&location=all&type=all&status-reserv=0&status=0&category=offline&limit=30&action=get/games'
                headers = {
                    'Accept': '*/*',
                    'Cookie': f'check_city=1; city={city_code};' + '_fbp=fb.1.1642578903089.4243748; _ym_visorc=w; jivosite_visit=237709; utm_referrer=https://quizium.ru/; utmstat_click_id=72e7b4d0345b8_8528661_5725183; sbjs_current=typ%3Dorganic%7C%7C%7Csrc%3Dgoogle%7C%7C%7Cmdm%3Dorganic%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29; sbjs_session=pgs%3D2%7C%7C%7Ccpg%3Dhttps%3A%2F%2Fquizium.ru%2Fschedule.html; sbjs_udata=vst%3D5%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Macintosh%3B%20Intel%20Mac%20OS%20X%2010_15_7%29%20AppleWebKit%2F605.1.15%20%28KHTML%2C%20like%20Gecko%29%20Version%2F14.1.2%20Safari%2F605.1.15; _ga=GA1.2.1001013549.1642578901; _gid=GA1.2.927698751.1642851611; _ym_isad=2; utmstat_session_start_at=1642944039; sbjs_history={%221%22:{%22src%22:%22google%22%2C%22trm%22:%22(none)%22%2C%22dt%22:%222022-01-19%22}%2C%222%22:{%22src%22:%22google%22%2C%22trm%22:%22(none)%22%2C%22dt%22:%222022-01-19%22}%2C%223%22:{%22src%22:%22google%22%2C%22trm%22:%22(none)%22%2C%22dt%22:%222022-01-19%22}%2C%224%22:{%22src%22:%22google%22%2C%22trm%22:%22(none)%22%2C%22dt%22:%222022-01-19%22}%2C%225%22:{%22src%22:%22google%22%2C%22trm%22:%22(none)%22%2C%22dt%22:%222022-01-19%22}%2C%22count%22:%225%22}; sbjs_current_add=fd%3D2022-01-22%2014%3A40%3A10%7C%7C%7Cep%3Dhttps%3A%2F%2Fquizium.ru%2F%7C%7C%7Crf%3Dhttps%3A%2F%2Fwww.google.com; _gcl_au=1.1.262462487.1642578902; _ym_d=1642578902; _ym_uid=1642578902375215138; utmstat_client_id=1642578902634862156; utmstat_hostname=quizium.ru; sbjs_first=typ%3Dorganic%7C%7C%7Csrc%3Dgoogle%7C%7C%7Cmdm%3Dorganic%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29; sbjs_first_add=fd%3D2022-01-19%2010%3A55%3A01%7C%7C%7Cep%3Dhttps%3A%2F%2Fquizium.ru%2F%7C%7C%7Crf%3Dhttps%3A%2F%2Fwww.google.com; sbjs_migrations=1418474375998%3D1; PHPSESSID=16f2d103b3a3e8253f78117bc6460fd9',
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
                                                                'card-kviz card-with-image card-kviz-standart']}):
            
                    dct = {}
                    dct['quiz'] = 'Квизиум'
                    date = column.find('span', 'date-kviz').text.lower()
                    if len(date.split(' ')[0]) == 1:
                        dct['date'] = '0' + date
                    else:
                        dct['date'] = date
                    dct['time'] = column.find('span', 'card-time-kviz').text
                    dct['name'] = column.find('span', 'title-card').text
                    dct['place'] = column.find('span', 'card-location-kviz').text
                    dct['reg'] = 'https://quizium.ru/' + column.find('a', 'link-game').get('href')

                    if (self.check_date(dct['date'])):
                        info.append(dct)
                    else:
                        break
            if quiz == 'WOW QUIZ' and quiz in self.quizes_incity:
                city_code = self.db.switch_city_name_codename(self.user_info[0][4], quiz)
                if city_code == 'wowquiz':
                    webpage = requests.get(f'https://wowquiz.ru/schedule#')
                else:
                    webpage = requests.get(f'https://{city_code}.wowquiz.ru/schedule#')
                soup = BeautifulSoup(webpage.text, 'html.parser')
                for column in soup.find_all('div', 'game-column'):
                    dct = {}
                    dct['quiz'] = 'WOW QUIZ'
                    dct['date'] = column.find('span', 'date').text
                    dct['time'] = column.find('span', 'time').text
                    dct['name'] = column.get('data-game_name')
                    dct['place'] = column.get('data-place_name')
                    dct['reg'] = f'https://{city_code}.wowquiz.ru/game/' + column.get('data-game_id')
                    if (self.check_date(dct['date'])):
                        info.append(dct)
                    else:
                        break

        print(f'Scraping - finished')
          
        #сортировка по дате
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
        
            
        return sorted_info

    def make_vote(self):
        options = []
        for game in self.get_info():
            text = ''
            for info in game.values():
                if 'http' not in info:
                    text += info + ' '
            options.append(text)
        options.append('Сори, ни одна из дат не подоходит...')
        return options

    
    def make_telegraph(self):

        data_list = self.get_info()
        telegraph = Telegraph(TOKEN_TELEGRAPH)
        if len(data_list) == 0:
            html_content = '<p>Сначала добавь в избранное хотя бы один квиз</p>'
        else:
            html_content = ''
            for game in data_list:
                html_content += f"<p>:white_check_mark:{game['date']}" + \
                    f"<br>:boom:{game['quiz']}" + \
                    f"<br>:speaker:{game['name']}" + \
                    f"<br>:round_pushpin:{game['place']}" + \
                    f"<br>:clock1:{game['time']}" + \
                    f"<br>{hlink('Зарегистрироваться', game['reg'])}" + \
                    f"<br><br></p>"
        html_content += f"<p>By {hlink('@quizerus_bot', 'https://t.me/quizerus_bot')}</p>"
        response = telegraph.create_page(
                author_name='Quizerus_bot',
                author_url='https://t.me/quizerus_bot',
                title='Расписание:', 
                html_content=emoji.emojize(html_content, use_aliases=True)
        )
        url = 'https://telegra.ph/{}'.format(response['path'])
        return url


#parser = Parser('227184505')
#print(parser.make_telegraph())

#parser.get_info('rnd')[0]
#print(parser.make_scheldue())
#for i in parser.get_info():
#    print(i)
#parser.make_vote()
#db = SQLighter('db_quiz.db')
#subscribers = db.get_subsctiptions('-1001642033822', sub_type='group_subscriptions')
#parser.make_telegraph(subscribers)