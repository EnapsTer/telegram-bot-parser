from config import *
import telebot
from telebot import types
from parser import HHParser
from bs4 import BeautifulSoup
import requests
import time

bot = telebot.TeleBot(TOKEN)
parser = HHParser(URL)
regions = {
    'Россия': 0,
    'Москва': 1,
    'Санкт-Петербург': 2,
    'Екатеринбург': 3,
    'Новосибирск': 4
}

@bot.message_handler(commands=['start'])
def start(message: types.Message):
    bot.send_sticker(message.from_user.id, STICKER)
    bot.send_message(message.from_user.id, "Вы спросите что умеет этот бот, "
                                           "я отвечу, он по вашему запросу найдет вам подходящие вакансии."
                                           "Может вы еще спросите, чем он лучше hh.ru или подобных сайтов, я отвечу, ничем🤷 \n\n"
                                           "Чтобы найти вакансию нажмите кнопку *'Поиск'*, если хотите выбрать регион, нажмите *'Настройки'*\n"
                                           "Чтобы начать все сначала введите команду *'/start'*, если вам нужна помощь *'/help'*\n\n*P.S*\n"
                                           "Если нашли ошибку, сообщите мне в личку, буду очень благодарен\n\n"
                                           "Разработал *Шагиджанян Андре*",
                     reply_markup=main_keyboard(), parse_mode='Markdown')



@bot.message_handler(content_types=['text'])
def buttons_handler(message: types.Message):
    if message.text ==  'Поиск':
        bot.send_message(message.from_user.id, "Введите название вакансии",reply_markup=main_keyboard())
    elif message.text == 'Настройки':
        bot.send_message(message.from_user.id, 'Выберите регион', reply_markup=area_keyboard())
    elif message.text in regions.keys():
        parser.set_url(area=regions[message.text])
        bot.send_message(message.from_user.id, "Введите название вакансии",reply_markup=main_keyboard())

    else:
        request_handler(message)


def request_handler(message: types.Message):
    if message.text == 'Далее':
        parser.set_url(page=1)
    elif message.text == 'Назад':
        parser.set_url(page=-1)
    else:
        parser.set_url(page=False, text=message.text)
        bot.send_message(message.from_user.id, f'*{parser.get_title()}* всего вакансий найдено в регионе *{parser.get_area()}*',
                         parse_mode="Markdown",
                         reply_markup=next_keyboard())
    result = parser.parse()

    for title, description in result:
        time.sleep(0)
        try:
            bot.send_message(message.from_user.id, f'*{title[0]}*\nЗарплата: *{title[1]}*\nКомпания: *{title[2].strip()}*\n_{description[3]}_\n\n'
                                                   f'{description[0]}\n{description[1]}',
                             reply_markup=inline_keyboard(description[2]), parse_mode="Markdown")
        except:
            continue

    bot.send_message(message.from_user.id, "Нажмите *'далее'*, чтобы перейти на другую страницу",parse_mode='Markdown')

def area_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    button1 = types.KeyboardButton("Россия")
    button2 = types.KeyboardButton("Москва")
    button3 = types.KeyboardButton("Санкт-Петербург")
    button4 = types.KeyboardButton("Екатеринбург")
    button5 = types.KeyboardButton("Новосибирск")
    keyboard.add(button1, button2, button3, button4, button5)
    return keyboard

def main_keyboard():
    main_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    search_button = types.KeyboardButton("Поиск")
    settings_button = types.KeyboardButton("Настройки")
    main_keyboard.add(search_button, settings_button)
    return main_keyboard

def inline_keyboard(url):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button = types.InlineKeyboardButton('Перейти', url=url)
    keyboard.add(button)
    return keyboard

def next_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    button1 = types.KeyboardButton("Далее")
    button2 = types.KeyboardButton("Назад")
    keyboard.add(button1, button2)
    return keyboard

if __name__ == '__main__':
     bot.polling(none_stop=True)

