from telegram_menu import BaseMessage, TelegramMenuSession, NavigationHandler


from telebot import types
from telebot.types import Message
import telebot
from secret_for_menu import API_KEY




bot= telebot.TeleBot(API_KEY)


@bot.message_handler(commands=['start'])
def start(message: Message):
    # save_user_info(message)
    # if check_for_access(message):
    # markup = types.ReplyKeyboardMarkup(row_width=2)
    # itembtn1 = types.KeyboardButton('a')
    # itembtn2 = types.KeyboardButton('v')
    # itembtn3 = types.KeyboardButton('d')
    # markup.add(itembtn1, itembtn2, itembtn3)
    # bot.send_message(message.chat_id, "Choose one letter:", reply_markup=markup)

    # or add KeyboardButton one row at a time:
    markup = types.ReplyKeyboardMarkup()
    itembtna = types.KeyboardButton('a')
    itembtnv = types.KeyboardButton('v')
    itembtnc = types.KeyboardButton('c')
    itembtnd = types.KeyboardButton('d')
    itembtne = types.KeyboardButton('e')
    markup.row(itembtna, itembtnv)
    markup.row(itembtnc, itembtnd, itembtne)
    bot.send_message(message.from_user.id, "Choose one letter:", reply_markup=markup)

        # bot.send_message(message.chat.id, my_process_py)



# Using the ReplyKeyboardMarkup class
# It's constructor can take the following optional arguments:
# - resize_keyboard: True/False (default False)
# - one_time_keyboard: True/False (default False)
# - selective: True/False (default False)
# - row_width: integer (default 3)
# row_width is used in combination with the add() function.
# It defines how many buttons are fit on each row before continuing on the next row.



bot.polling(none_stop=True)