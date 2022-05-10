import asyncio
import logging
import time
import pytz
import os

from dotenv import load_dotenv
from tinkoff.invest import Client, CandleInstrument, SubscriptionInterval, OperationState
from tinkoff.invest.services import MarketDataStreamManager, InstrumentIdType
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, InlineKeyboardMarkup, \
    InlineKeyboardButton, BotCommand
from keyboard import main_menu, trade_menu, exchange, menu, to_menu
from datetime import datetime, timedelta
from tinkoff.invest.utils import now

"""
TODO: деление акций по биржам
      тикер в операциях и позициях
      логи
      время сделок и операций поменять
"""
load_dotenv()

TOKEN = os.getenv('TOKEN')
TG_API_TOKEN = os.getenv('TG_BOT_TOKEN')
tg_user_id = os.getenv('TG_USER_ID')
tinkoff_account_id = os.getenv('TINKOFF_ACCOUNT_ID')

favourite_stocks = {}
stocks = []
favourite_menu_ticker = []
tmp = []

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
bot = Bot(token=TG_API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    commands = [
        BotCommand(command="/start", description="Начать диалог с ботом"),
        BotCommand(command="/trade", description="Режим торговли"),
        BotCommand(command="/help", description="Информация о проекте и боте")
    ]
    await bot.set_my_commands(commands)
    await message.answer(
        'Добро пожаловать в торговый терминал в Telegram\nДля того что бы посмотреть мои возможности нажми /help\n'
        'Если хочешь начать торговать нажми /trade')
    logging.info(f'User: {message.from_user.first_name} start dialogue with bot')


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.answer('Soon...')
    logging.info(f'User: {message.from_user.first_name} requested command HELP')


@dp.message_handler(commands=['trade'])
async def trade(message: types.Message):
    logging.info(f'User: {message.from_user.first_name} started trading')
    start_message = await message.answer('Вы перешли в режим торгов')
    time.sleep(2)
    await bot.delete_message(tg_user_id, start_message.message_id)
    await bot.delete_message(tg_user_id, start_message.message_id - 1)
    await message.answer('Меню', reply_markup=main_menu)


@dp.callback_query_handler(text='back_btn')
async def back(query: CallbackQuery):
    logging.info(f'User: {query.from_user.first_name} go to main menu')
    await query.message.edit_text('Меню', reply_markup=main_menu)


@dp.callback_query_handler(text='btn_1')
async def get_portfolio(message: types.Message):
    with Client(TOKEN) as client:
        logging.info('getting positions of users portfolio')
        try:
            portfolio = client.operations.get_portfolio(account_id=tinkoff_account_id)
            logging.info(portfolio)
            profit = portfolio.expected_yield.units + (portfolio.expected_yield.nano / pow(10, 9))
            t_amount_shares = portfolio.total_amount_shares.units + (portfolio.total_amount_shares.nano / pow(10, 9))
            t_amount_bonds = portfolio.total_amount_bonds.units + (portfolio.total_amount_bonds.nano / pow(10, 9))
            t_amount_etf = portfolio.total_amount_etf.units + (portfolio.total_amount_etf.nano / pow(10, 9))
            t_amount_currencies = portfolio.total_amount_currencies.units + (
                    portfolio.total_amount_currencies.nano / pow(10, 9))
            t_amount_futures = portfolio.total_amount_futures.units + (portfolio.total_amount_futures.nano / pow(10, 9))
            await bot.send_message(tg_user_id, f'Текущая относительная доходность портфеля, в %: {profit}\n'
                                                         f'Cтоимость акций в портфеле в рублях: {t_amount_shares}\n'
                                                         f'Cтоимость облигаций в портфеле в рублях: {t_amount_bonds}\n'
                                                         f'Cтоимость фондов в портфеле в рублях: {t_amount_etf}\n'
                                                         f'Cтоимость валют в портфеле в рублях: {t_amount_currencies}\n'
                                                         f'Cтоимость фьючерсов в портфеле в рублях: {t_amount_futures}')
            time.sleep(1)
            positions = portfolio.positions
            for position in positions:
                # ticker = client.instruments.share_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI,
                #                                      id=position).instrument.ticker
                a_position_price = position.average_position_price.units + (
                        position.average_position_price.nano / pow(10, 9))
                ex_yield = position.expected_yield.units + (position.expected_yield.nano / pow(10, 9))
                q_lots = position.quantity_lots.units + (position.quantity_lots.nano / pow(10, 9))
                current_price_instrument = position.current_price.units + (
                        position.current_price.nano / pow(10, 9)) * q_lots
                await bot.send_message(tg_user_id, 'Позиции:\n'
                                                             f'Тикер: {position.figi}\n'
                                                             f'{a_position_price} -> {current_price_instrument}\n'
                                                             f'Стоимость бумаг в портфеле'
                                                             f'{round(q_lots * current_price_instrument, 2)}\n'
                                                             f'{ex_yield} ({round(((a_position_price / current_price_instrument) * 100) - 100, 2)})')
        except Exception as e:
            logging.error(f'Error while requesting portfolio, error: {e}')

        time.sleep(0.5)
        await bot.send_message(tg_user_id, 'Меню', reply_markup=main_menu)


@dp.callback_query_handler(text='btn_4')
async def btn1(query: CallbackQuery):
    logging.info('User goes to the trade menu')
    await query.message.edit_text('Выберете один из пунктов в меню', reply_markup=trade_menu)


@dp.callback_query_handler(text='favourites')
async def load_all_stocks(query: CallbackQuery):
    logging.info('Loading SPB stocks')
    with Client(TOKEN) as client:
        stocks_ = client.instruments.shares().instruments
        for stock in stocks_:
            stocks.append(stock.figi)
        logging.info('End loading, ready for working')
    if len(favourite_stocks) == 0:
        await query.message.edit_text(
            'В избранном пока нет ни одной акции, что бы добавить нажмите на кнопку "Ввести тикер"',
            reply_markup=menu)
    else:
        for ticker in tmp:
            buttons = []
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            while len(tmp) > 0:
                buttons.append(InlineKeyboardButton(text=ticker, callback_data='123'))
                tmp.remove(ticker)
            keyboard.add(*buttons)
            await query.message.answer("Избранное", reply_markup=keyboard)


@dp.callback_query_handler(text='menu')
async def go_to_trade_menu(query: CallbackQuery):
    logging.info('back to the trade menu')
    await query.message.edit_text('Меню', reply_markup=trade_menu)


@dp.callback_query_handler(text='add')
async def add_stock(query: CallbackQuery):
    logging.info(f'User: {query.from_user.first_name} added new tikcer to favourite')
    await query.message.edit_text('Вводите тикер большими буквами\nПример: AAPL')


@dp.callback_query_handler(text='favourites_menu')
async def favourites_menu(message: types.Message):
    logging.info(f'User: {message.from_user.first_name} requested favourites')
    await bot.send_message(tg_user_id, f'FAVOURITES: {favourite_stocks}')


@dp.callback_query_handler(text='operations')
async def get_operations(message: types.Message):  # add try catch state
    with Client(TOKEN) as client:
        operations = client.operations.get_operations(account_id=tinkoff_account_id, from_=now() - timedelta(days=56),
                                                      to=now(),
                                                      ).operations

        for operation in operations:
            currency_operation = operation.currency
            payment_operation = operation.payment.units + (operation.payment.nano / pow(10, 9))
            price_operation = operation.price.units + (operation.price.nano / pow(10, 9))
            quantity_operation = operation.quantity
            ticker = operation.figi
            date_operation = datetime.strptime(operation.date.strftime("%Y-%m-%d %H:%M:%S"),
                                               "%Y-%m-%d %H:%M:%S") + timedelta(hours=3)
            for trade in operation.trades:
                q_trade = trade.quantity
                date_trade = datetime.strptime(trade.date_time.strftime("%Y-%m-%d %H:%M:%S"),
                                               "%Y-%m-%d %H:%M:%S") + timedelta(hours=3)
                price_trade = trade.price.units + (trade.price.nano / pow(10, 9))
                if payment_operation >= 0:  # продажа
                    await bot.send_message(tg_user_id, 'Операция:\n'
                                                                 f'Дата: {date_operation}\n'
                                                                 f'Продажа {quantity_operation} лотов {ticker}\n'
                                                                 f'+{payment_operation}\n'
                                                                 f'Цена продажи: {round(price_operation, 2)} {currency_operation}\n\n'
                                                                 f'Колличество сделок: {len(operation.trades)}\n'
                                                                 f'{date_trade}\t\t{q_trade}шт. по {price_trade}\n'
                                                                 f'\n\n\n')
                    time.sleep(0.2)
                else:  # покупка
                    await bot.send_message(tg_user_id, 'Операция:\n'
                                                                 f'Дата: {date_operation}\n'
                                                                 f'Покупка {quantity_operation} лотов {ticker}\n'
                                                                 f'{payment_operation}\n'
                                                                 f'Цена покупки: {round(price_operation, 2)} {currency_operation}\n\n'
                                                                 f'Колличество сделок: {len(operation.trades)}\n'
                                                                 f'{date_trade}\t\t{q_trade}шт. по {price_trade}\n')
                    time.sleep(0.2)
    time.sleep(0.5)
    await bot.send_message(tg_user_id, 'Меню', reply_markup=trade_menu)


@dp.callback_query_handler(text='requests')
async def get_active_orders(query: CallbackQuery):
    logging.info('get active orders')
    with Client(TOKEN) as client:
        orders = client.orders.get_orders(account_id=tinkoff_account_id)
        if len(orders.orders) == 0:
            await query.message.answer('У вас нет активных заявок')
            logging.info('there is no active orders')
        else:
            await query.message.answer('Запрашивает активные заявки')
            logging.info('request active orders')


@dp.message_handler()
async def main(message: types.Message):
    logging.info(f'[MAIN THREAD]: {message.text}')
    tick = message.text
    await add_to_favourites(tick)


def check(ticker: str) -> bool:
    if ticker not in favourite_stocks.keys():
        return True
    else:
        return False


async def add_to_favourites(tick: str):
    with Client(TOKEN) as client:

        instrument = client.instruments.share_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER,
                                                 id=tick, class_code='SPBXM').instrument
        logging.info(f'[INSTRUMENT]: {instrument}')
        if check(instrument.ticker):
            if len(favourite_stocks) <= 10:
                favourite_stocks[instrument.ticker] = instrument.figi
                tmp.append(instrument.ticker)
                logging.info(favourite_stocks)
                await bot.send_message(tg_user_id, 'Акция успешно добавлена', reply_markup=to_menu)
            else:
                await bot.send_message(tg_user_id,
                                       'Достигнуто максимально колличсетво акций в избранном\nЧто бы удалить акцию нажмите на кнопку ниже',
                                       reply_markup=to_menu)
                logging.info('max size of favourites')
        else:
            await bot.send_message(tg_user_id, 'Акция уже в избранном')
            logging.info('stock already in favourites')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
