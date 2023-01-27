from datetime import datetime, timedelta
from decimal import Decimal
from pony.orm import *

db = Database()

class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    user_id = Required(Decimal, unique=True)
    username = Optional(str, unique=True)
    first_name = Optional(str, nullable=True)
    last_name = Optional(str, nullable=True)
    city = Optional(str, default="Москва")
    timerange = Optional(str, default='неделя')
    team = Optional(str, default="Не указана")
    group_id = Optional(int, nullable=True)
    first_login = Optional(datetime, default=lambda: datetime.now())
    quizs = Set('Quiz')
    daily_quiz = Optional('Daily_quiz')


class Quiz(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    codename = Required(str)
    city = Required(str)
    city_code = Required(str)
    users = Set(User)


class Daily_quiz(db.Entity):
    id = PrimaryKey(int, auto=True)
    user = Required(User)
    score = Optional(int, default=0)
    daily_score = Optional(int, default=0)
    fifty = Optional(bool, default=True)
    mistake = Optional(bool, default=True)
    last_game = Optional(datetime, default=lambda: datetime.now() - timedelta(days=1))

