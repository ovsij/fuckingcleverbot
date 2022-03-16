
from fuzzywuzzy import process
import psycopg2
from config import *
from datetime import datetime, timedelta

class Postgres:

    def __init__(self):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = psycopg2.connect(
            database=database, 
            user=user, 
            password=password, 
            host=host, 
            port=port)
        self.cursor = self.connection.cursor()
        


    def add_subscriber(self, user_id, user_name, first_name, last_name, city, first_login):
        """Добавляем подписчика"""
        with self.connection:
            return self.cursor.execute("INSERT INTO public.subscribers \
                (user_id,user_name,first_name,last_name,city,first_login) \
                VALUES(%s,%s,%s,%s,%s,%s)", (user_id, user_name, first_name, last_name, city, first_login))
            
    def subscriber_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            self.cursor.execute('SELECT * FROM public.subscribers WHERE user_id = %s', (user_id,))
            return bool(len(self.cursor.fetchall()))

    def add_subscription(self, user_id, user_name='Null', group_id=0, quiz='Null'):
        """Добавляем нового подписчика"""
        with self.connection:
            self.cursor.execute(f"INSERT INTO public.subscriptions \
                    (user_id, user_name, group_id, quiz) \
                        VALUES(%s,%s,%s,%s)", (user_id, user_name, group_id, quiz))
            
    def update_subscription(self, user_id, new_quiz, old_quiz='Null'):
        """Обновляем статус подписки пользователя"""
        with self.connection:
            self.cursor.execute(f"UPDATE public.subscriptions SET quiz = %s WHERE user_id = %s AND quiz = %s", (new_quiz, user_id, old_quiz))

    def get_subscriptions(self, user_id):
        with self.connection:
            self.cursor.execute(f'SELECT * FROM subscriptions WHERE user_id = %s', (int(user_id),))
            return self.cursor.fetchall()
        

    def delete_subscription(self, user_id, quiz):
        if len(self.get_subscriptions(user_id)) > 1:
            with self.connection:
                return self.cursor.execute(f"DELETE FROM public.subscriptions WHERE user_id = %s AND quiz = %s", (user_id,quiz))
        else:
            with self.connection:
                return self.cursor.execute(f"UPDATE public.subscriptions SET quiz = 'Null' WHERE user_id = %s AND quiz = %s", (user_id,quiz))
    
    def update_timerange(self, user_id, time_range):
        with self.connection:
            return self.cursor.execute("UPDATE public.subscribers SET timerange = %s WHERE user_id = %s", (time_range, user_id))
    
    def update_group(self, user_id, group_id):
        with self.connection:
            return self.cursor.execute("UPDATE public.subscriptions SET group_id = %s WHERE user_id = %s", (group_id, user_id))
    
    def check_group(self, user_id):
        with self.connection:
            try:
                self.cursor.execute("SELECT group_id FROM subscriptions WHERE user_id = %s", (user_id,))
                if self.cursor.fetchall()[0][0] != 0:
                    return True
                else:
                    return False
            except:
                return False
    
    def get_subscribers(self):
        with self.connection:
            self.cursor.execute("SELECT user_id FROM public.subscribers")
            return [i[0] for i in self.cursor.fetchall()]

    def get_user_info(self, user_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM public.subscribers WHERE user_id = %s", (user_id,))
            return [i for i in self.cursor.fetchall()]
    
    def check_city(self, input_city):
        with self.connection:
            self.cursor.execute("SELECT name FROM public.cities")
            cities = [city[0] for city in self.cursor.fetchall()]
            match_city = process.extractOne(input_city.lower(), cities)
            if match_city[1] > 60 and len(input_city) - len(match_city[0]) <= 3 and input_city[0].lower() == match_city[0][0].lower():
                return match_city[0]
            else:
                return False

    def update_city(self, user_id, city):
        with self.connection:
            return self.cursor.execute(
                "UPDATE public.subscribers SET city = %s WHERE user_id = %s", 
                (city, user_id))

    def get_quizes_incity(self, user_id):
        with self.connection:
            self.cursor.execute(
                "SELECT quiz FROM cities WHERE \
                name = (SELECT city FROM subscribers WHERE \
                user_id = %s)", (user_id,))
            names = [i[0] for i in self.cursor.fetchall()]
            code_names = []
            for i in names:
                self.cursor.execute("SELECT code_name FROM all_quizes \
                WHERE name = %s", (i,))
                code_names.append(self.cursor.fetchall()[0][0])
            return names, code_names
    
    def switch_codename_name(self, code_name):
        with self.connection:
            self.cursor.execute(
                "SELECT name FROM all_quizes WHERE code_name = %s",
                (code_name,))
            name = self.cursor.fetchall()
            return name

    def switch_city_name_codename(self, name, quiz):
        with self.connection:
            self.cursor.execute(
                "SELECT code_name FROM cities WHERE name = %s AND quiz = %s", (name, quiz))
            code_name = self.cursor.fetchall()[0][0]
            return code_name

    def get_unavaliable_quizes(self, quizes):
        with self.connection:
            self.cursor.execute(
                "SELECT name FROM all_quizes WHERE NOT name in \
                (SELECT quiz FROM cities)")
            unav_quizes = [i[0] for i in self.cursor.fetchall() if i[0] in [q[4] for q in quizes]]
            print([q[4] for q in quizes])
            return unav_quizes

    def add_log(self, user_id, time, action):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO logs (user_id, time, action) \
                VALUES(%s,%s,%s)", (user_id, time, action))
            

    def link_exists(self, user_id):
        with self.connection:
            self.cursor.execute('SELECT schedule FROM subscribers WHERE user_id = %s', (user_id,))
            result = self.cursor.fetchall()
            if 'ERROR' in result[0][0]:
                return False
            else:
                return True

    def link_update(self, user_id, url):
        with self.connection:
            self.cursor.execute('UPDATE subscribers SET schedule = %s WHERE user_id = %s', (url, user_id))
        return url 
    
    def update_team(self, user_id, team):
        return self.cursor.execute('UPDATE subscribers SET team = %s WHERE user_id = %s', (team, user_id))
        

    def close(self):
        """Закрываем соединение с БД"""
        self.cursor.close()
        self.connection.close()
        


db = Postgres()
print(db.get_subscriptions('227184505'))
#sub = db.get_subscriptions('rostov')
#print(sub)
#print([i[4] for i in db.get_subscriptions('227184505')])
#print(db.get_unavaliable_quizes(db.get_subsctiptions('2211')))
#db.add_subscriber('1111', 'ugiйu', 'Смузи', 'Смузи', 'Ростов-на-Дону', datetime.now())
#print(db.get_user_info('227184505'))
#db.add_subscription('227184505')
#print(db.get_subscriptions('227184505'))
#print([quiz[3] for quiz in db.get_subscriptions('227184505')])
#print(db.get_user_quizes('-1001642033822', sub_type='group_subscriptions'))
#db.link_create('111', 'https://telegra.ph/Raspisanie-01-28-9')

