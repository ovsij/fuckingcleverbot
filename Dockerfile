FROM python:3.11.0
COPY . .
RUN pip3 install -r requirements.txt
CMD python bot/bot.py
