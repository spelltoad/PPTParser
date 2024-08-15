import telebot
from telebot import types
from parser import PTParser

bot = telebot.TeleBot('7353813520:AAFtdwQIJHsAYMeTIMWbrRg1bYLswGATO_M')
user_states = {}
parser = PTParser()

@bot.message_handler(commands=['start'])
def handle_start(message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton('Получить расписание', callback_data='get')
    button2 = types.InlineKeyboardButton('Обновить расписание', callback_data='update')
    button3 = types.InlineKeyboardButton('Список маршрутов', callback_data='info')
    keyboard.add(button1, button2, button3)
    bot.send_message(message.chat.id, 
"""PermPublicTransport info.

Бот для получения расписания отправлений с конечных остановок общественного транспорта города Перми.""", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    choice = call.data
    user_states[user_id] = choice
    if choice == "get":
        bot.send_message(chat_id, "Введите номера маршрутов для получения информации об отправлениях")
        user_states[user_id] = "get"
    elif choice == "update":
        bot.send_message(chat_id, "Введите номера маршрутов для обновления")
    elif choice == "info":
        bot.send_message(chat_id, parser.listRoutes("bus"))
    else:
        pass

@bot.message_handler(func=lambda message: message.from_user.id in user_states)
def handle_user_input(message):
    user_id = message.from_user.id
    state = user_states[user_id]
    input_data = message.text
    numbers = input_data.split(',')
    numbers = [num.strip() for num in numbers]
    if state == "get":
        messages = parser.showTerminae(numbers, "bus").split('\n\n')
        for i in messages:
            if i:
                bot.send_message(message.chat.id, i, parse_mode="html")
                continue
    elif state == "update":
        bot.send_message(message.chat.id, parser.checkTerminae(numbers), parse_mode="html")
    else:
        pass

bot.polling()