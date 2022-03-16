from parser import Parser
from database import SQLighter
import sqlite3
import requests
from bs4 import BeautifulSoup
import re

connection = sqlite3.connect('db_quiz.db')
cursor = connection.cursor()

with connection:
    code_city_names = [i[0] for i in cursor.execute('SELECT code_name FROM cities WHERE quiz = "Квиз, плиз!"').fetchall()]
    
info = []
for city in code_city_names:
    url = f'https://{city}.quizplease.ru/schedule'
    webpage = requests.get(url)
    soup = BeautifulSoup(webpage.text, 'html.parser')
    
    for column in soup.find_all('div', 'schedule-column'):
        dct = {}
        dct['quiz'] = 'Квиз, Плиз!'
        dct['date'] = column.find(True, {'class': ['h3 h3-green h3-mb10', 
                                                                'h3 h3-pink h3-mb10', 
                                                                'h3 h3-yellow h3-mb10']}).text.split(', ')[0]
        for block in column.find_all('div', 'schedule-info'):
            if re.search(r'\d\d.\d\d', block.text.strip('\n')):
                dct['time'] = block.text.strip('\n')
        dct['name'] = column.find('div', 'h2 h2-game-card h2-left').text
        dct['place'] = column.find('div', 'schedule-block-info-bar').text\
                                        .strip('\t').strip(' ')\
                                        .rstrip('\tИнфа о баре\n')
    info.append(dct)
    print(f'{city} is done')

print(len(info))