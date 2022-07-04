import time
import telebot
import sqlite3
import datetime
from telebot import types
token = '5357006547:AAFAFX8yJVb5w14LzMF0OHoGEuX-jbDhP6c'
bot = telebot.TeleBot(token)
connect = sqlite3.connect('users2.db')
cursor = connect.cursor()
ad = cursor.execute(f"SELECT id_admin FROM admins")
ad_ = cursor.fetchall()
for result in ad_:
    a = [int(result[0])]



@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id not in a:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('Подписаться на рассылку')
        markup.add(item1)
        bot.send_message(message.chat.id, 'Привет, я бот Михаил! И я буду вам напоминать про занятия!',reply_markup=markup)
        connect0 = sqlite3.connect('users2.db')
        cursor0 = connect0.cursor()
        cursor0.execute("""CREATE TABLE IF NOT EXISTS teachers_id(id INTEGER, teacher TEXT, permission TEXT)""")
        connect0.commit()


        # регистрируем пользователя в бд ниже

        cursor0.execute(f"SELECT id FROM teachers_id WHERE id = {message.chat.id}")
        data = cursor0.fetchone()
        text = message.from_user.username
        connect0.commit()

        if data is None:
            user_id = message.chat.id
            cursor0.execute("INSERT INTO teachers_id VALUES(?,?);", (str(user_id), str(text)))
            connect0.commit()
        else:
            bot.send_message(message.chat.id, 'Вы уже зарегистрированы!')

    else:
        bot.send_message(message.chat.id, 'Вы админ')

#ограничиваем права пользователей
@bot.message_handler(func=lambda message: message.chat.id not in a, commands=['delete', 'add'])
def some(message):
    bot.send_message(message.chat.id, 'Отказано в доступе')

#добавляем команду "добавить"
@bot.message_handler(commands=['add'])
def add(message):
    msg = bot.send_message(message.chat.id, 'Введите айди пользователя')
    bot.register_next_step_handler(msg, after_text2)

#добавляем команду "удалить"
@bot.message_handler(commands=['delete'])
def delete(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Себя')
    item2 = types.KeyboardButton('Удалить пользователя по айди')
    markup.add(item1, item2)
    mmg = bot.send_message(message.chat.id, 'Кого вам нужно удалить?', reply_markup=markup)
    bot.edit_message_reply_markup(message.chat.id, mmg, reply_markup=None)

#регистрируем все кнопки и команды
@bot.message_handler(content_types=['text'])
def func(message):
    connect1 = sqlite3.connect('users2.db')
    cursor1 = connect1.cursor()
    del_key = types.ReplyKeyboardRemove()
    if message.text == 'Себя':
        cursor1.execute(f"DELETE FROM teachers_id WHERE id = {message.chat.id}")
        bot.send_message(message.chat.id, 'Пользователь удалён', reply_markup=del_key)
        connect1.commit()
    elif message.text == 'Удалить по айди':
        msg = bot.send_message(message.chat.id, 'Введите айди пользователя', reply_markup=del_key)
        bot.register_next_step_handler(msg, after_text)
    elif message.text == 'Подписаться на рассылку':
        bot.send_message(message.chat.id, 'Вы подписались на рассылку!',reply_markup=del_key)
        while True:
            connect_ = sqlite3.connect('users2.db')
            cursor_ = connect_.cursor()
            current_time = time.time()
            max_time = current_time + 86400
            lessons = cursor_.execute(
                f"SELECT lessons.*, teachers_id.id FROM lessons, teachers_id WHERE teachers_id.id = lessons.id "
                f"AND lessons.data < {max_time} AND lessons.data > {current_time}").fetchall()
            connect_.commit()
            for lesson in lessons:
                lesson_time = time.gmtime(lesson[2])
                bot.send_message(lesson[4], f"У вас занятие по предмету {lesson[1]} завтра в {lesson_time.tm_hour}:{lesson_time.tm_min}")
            time.sleep(86400)
    else:
        bot.send_message(message.chat.id, 'Я вас не понимаю')


def after_text(message):
    connect2 = sqlite3.connect('users2.db')
    cursor2 = connect2.cursor()
    cursor2.execute(f"SELECT id FROM teachers_id WHERE id = {message.text}")
    del_us = cursor2.fetchone()
    if str(del_us) != 'None':
        cursor2.execute(f"DELETE FROM teachers_id WHERE id = {message.text}")
        bot.send_message(message.chat.id, 'Пользователь удалён')
        connect2.commit()
    else:
        bot.send_message(message.chat.id, 'Я вас не понял')


def after_text2(message):
    if message.text.isdigit():
        connect3 = sqlite3.connect('users2.db')
        cursor3 = connect3.cursor()
        cursor3.execute(f"INSERT INTO teachers_id VALUES(?,?);",
                        (str(message.text), 'добавленный по айди пользователь'))
        bot.send_message(message.chat.id, 'Пользователь добавлен')
        connect3.commit()
    else:
        bot.send_message(message.chat.id, 'Я вас не понимаю')


bot.polling(none_stop=True)
