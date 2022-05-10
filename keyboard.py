from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

main_menu = InlineKeyboardMarkup(row_width=1)
first_btn = InlineKeyboardButton(text='Портфель', callback_data='btn_1')
# second_btn = InlineKeyboardButton(text='Активные заявки', callback_data='btn_2')
# third_btn = InlineKeyboardButton(text='Операции', callback_data='btn_3')
fourth_btn = InlineKeyboardButton(text='Торговать', callback_data='btn_4')
# back_btn = InlineKeyboardButton(text='Меню', callback_data='back_btn')
main_menu.insert(first_btn)
# main_menu.insert(second_btn)
# main_menu.insert(third_btn)
main_menu.insert(fourth_btn)
# main_menu.insert(back_btn)

trade_menu = InlineKeyboardMarkup(row_width=1)
fav_stocks = InlineKeyboardButton(text='Избранное', callback_data='favourites')
operations = InlineKeyboardButton(text='Операции', callback_data='operations')
active_req = InlineKeyboardButton(text='Активные заявки', callback_data='requests')
choose = InlineKeyboardButton(text='Выбрать инструмент', callback_data='choose')
back_btn = InlineKeyboardButton(text='Меню', callback_data='back_btn')
trade_menu.insert(fav_stocks)
trade_menu.insert(operations)
trade_menu.insert(active_req)
trade_menu.insert(choose)
trade_menu.insert(back_btn)

exchange = InlineKeyboardMarkup(row_width=2)
all_stocks = InlineKeyboardButton(text='Избранное', callback_data='favourites_menu')
exchange.insert(all_stocks)
exchange.insert(back_btn)

# full_favourites = InlineKeyboardMarkup(row_width=1)
# delete = InlineKeyboardButton('Удалить акицю', callback_data='delete')

menu = InlineKeyboardMarkup(row_width=2)
add_favourites = InlineKeyboardButton(text='Ввести тикер', callback_data='add')
menu.insert(add_favourites)
menu.insert(back_btn)


to_menu = InlineKeyboardMarkup(row_width=1)
button = InlineKeyboardButton('Перейти в меню', callback_data='menu')

to_menu.insert(button)
