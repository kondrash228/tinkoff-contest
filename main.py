import asyncio
import time

from tinkoff.invest import Client, CandleInstrument, SubscriptionInterval
from tinkoff.invest.services import MarketDataStreamManager, InstrumentIdType
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
import logging
from keyboard import main_menu, trade_menu, exchange, menu, to_menu

"""
TODO: деление акций по биржам
"""

TOKEN = 't.BLtZWmlj_Raj-77CQuiflaKQQerwa1MSn56eO_AulW8X2QcC24Bb5RiBF_rjQdzNORfzTEhGmfdJoJeezyu-xQ'
API_TOKEN = '1993104882:AAHEGfoWyrSZaot8l8MMoblgrMaiBPo9cWY'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
ID = 802693897
taccount_id = '2097214379'

stocks_ = {}
favourite_stocks = {}
stocks_spb = []
stocks_moex = []
favourite_menu_ticker = []

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
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
    start_message = await message.answer('Вы перешли в режим торгов')
    time.sleep(2)
    await bot.delete_message(message.from_user.id, start_message.message_id)
    await bot.delete_message(message.from_user.id, start_message.message_id - 1)
    await message.answer('Меню', reply_markup=main_menu)
    logging.info(f'User: {message.from_user.first_name} started trading')


@dp.callback_query_handler(text='back_btn')
async def back(query: CallbackQuery):
    await query.message.edit_text('Меню', reply_markup=main_menu)


@dp.callback_query_handler(text='btn_1')
async def get_portfolio(message: types.Message):
    with Client(TOKEN) as client:
        portfolio = client.operations.get_portfolio(account_id=taccount_id)
        logging.info(portfolio)
        profit = portfolio.expected_yield.units + (portfolio.expected_yield.nano / pow(10,9))
        t_amount_shares = portfolio.total_amount_shares.units + (portfolio.total_amount_shares.nano / pow(10,9))
        t_amount_bonds = portfolio.total_amount_bonds.units + (portfolio.total_amount_bonds.nano / pow(10,9))
        t_amount_etf = portfolio.total_amount_etf.units + (portfolio.total_amount_etf.nano / pow(10,9))
        t_amount_currencies = portfolio.total_amount_currencies.units + (portfolio.total_amount_currencies.nano / pow(10,9))
        t_amount_futures = portfolio.total_amount_futures.units + (portfolio.total_amount_futures.nano / pow(10,9))
        await bot.send_message(message.from_user.id, f'Текущая относительная доходность портфеля, в %: {profit}\n'
                                                     f'Общая стоимость акций в портфеле в рублях: {t_amount_shares}\n'
                                                     f'Общая стоимость облигаций в портфеле в рублях: {t_amount_bonds}\n'
                                                     f'Общая стоимость фондов в портфеле в рублях: {t_amount_etf}\n'
                                                     f'Общая стоимость валют в портфеле в рублях: {t_amount_currencies}\n'
                                                     f'Общая стоимость фьючерсов в портфеле в рублях: {t_amount_futures}')
        time.sleep(1)
        positions = portfolio.positions
        for position in positions:
            figi = position.figi
            t_instrument = position.instrument_type
            lots_quantity = position.quantity.units + (position.quantity.nano / pow(10,9))
            a_position_price = position.average_position_price.units + (position.average_position_price.nano / pow(10,9))
            ex_yield = position.expected_yield.units + (position.expected_yield.nano / pow(10,9))
            av_position_price_pt = position.average_position_price_pt.units + (position.average_position_price_pt.nano / pow(10,9))
            current_price_instrument = position.current_price.units + (position.current_price.nano / pow(10,9))
            q_lots = position.quantity_lots.units + (position.quantity_lots.nano / pow(10,9))
            await bot.send_message(message.from_user.id, 'Позиции:\n'
                                                         f'Фиги: {figi}\n'
                                                         f'Тип инструмента: {t_instrument}\n'
                                                         f'Количество инструмента в портфеле в штуках: {lots_quantity}\n'
                                                         f'Средневзвешенная цена позиции. Возможна задержка до секунды для пересчёта: {a_position_price}\n'
                                                         f'Текущая рассчитанная относительная доходность позиции, в %: {ex_yield}\n'
                                                         f'Средняя цена лота в позиции в пунктах (для фьючерсов). Возможна задержка до секунды для пересчёта: {av_position_price_pt}\n'
                                                         f'Текущая цена за 1 инструмент. Для получения стоимости лота требуется умножить на лотность инструмента: {current_price_instrument}\n'
                                                         f'Количество лотов в портфеле: {q_lots}')


@dp.callback_query_handler(text='btn_4')
async def btn1(query: CallbackQuery):
    await query.message.edit_text('Выберете один из пунктов в меню', reply_markup=trade_menu)


@dp.callback_query_handler(text='favourites')
async def add_favourite(query: CallbackQuery):
    await query.message.edit_text('Выберете биржу или посмотрите свои избранные', reply_markup=exchange)


@dp.callback_query_handler(text='spb')
async def spb_exchange(query: CallbackQuery):
    logging.info('Loading SPB stocks')

    with Client(TOKEN) as client:
        stocks = client.instruments.shares().instruments
        for stock in stocks:
            if stock.exchange == 'SPB':
                stocks_spb.append(stock.figi)

        logging.info('End loading, ready for working')
        await query.message.edit_text(
            'Список доступных акций загружен, для того что бы добавить акцию в избранное, нажмите на кнопку "Ввести тикер"\n*Максимально колличество акций в избранном 10',
            reply_markup=menu)


@dp.callback_query_handler(text='msc')
async def msc_exchange(query: CallbackQuery):
    logging.info('Loading MOEX stocks')

    with Client(TOKEN) as client:
        stocks = client.instruments.shares().instruments

        for stock in stocks:
            if stock.exchange == 'MOEX':
                stocks_moex.append(stock.figi)
        logging.info('End loading, ready for working')
        await query.message.edit_text(
            'Список доступных акций загружен, для того что бы добавить акцию в избранное, нажмите на кнопку "Ввести тикер"\n*Максимально колличество акций в избранном 10',
            reply_markup=menu)


@dp.callback_query_handler(text='delete')
async def delete_stock(message: types.Message):
    await bot.send_message(message.from_user.id, 'Выберите тикер той акции которую хотите удалить')
    await bot.send_message(message.from_user.id, f'{favourite_stocks}')
    logging.info(f'[DELETE THREAD]: {message}')
    for ticker in favourite_menu_ticker:
        await bot.send_message(message.from_user.id, f'Избранное:\n{ticker}')


@dp.callback_query_handler(text='menu')
async def go_to_trade_menu(query: CallbackQuery):
    await query.message.edit_text('Меню', reply_markup=trade_menu)


@dp.callback_query_handler(text='add')
async def add_stock(query: CallbackQuery):
    await query.message.edit_text('Вводите тикер большими буквами\nПример: AAPL')


@dp.callback_query_handler(text='favourites_menu')
async def favourites_menu(message: types.Message):
    await bot.send_message(message.from_user.id, f'FAVOURITES: {favourite_stocks}')


@dp.message_handler()
async def main(message: types.Message):
    logging.info(f'[MAIN THREAD]: {message.text}')
    markup = types.ReplyKeyboardRemove()
    if message.text == 'Ввести тикер':
        await bot.send_message(message.from_user.id, 'Вводите тикер большими буквами\nПример: AAPL',
                               reply_markup=markup)
    tick = message.text
    await add_to_favourites(tick)
    # elif message.text == 'Пропустить':
    #     await bot.delete_message(message.from_user.id, message.message_id - 1)
    #     await bot.send_message(message.from_user.id, 'Меню',
    #                            reply_markup=trade_menu)
    # if message.text == 'Удалить акцию':
    #     await bot.send_message(message.from_user.id, 'Выберите тикер той акции которую хотите удалить')
    #     await bot.send_message(message.from_user.id, f'{favourite_stocks}')


async def delete_from_favourites(ticker: str):
    del favourite_stocks[ticker]


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
                logging.info(favourite_stocks)
                await bot.send_message(ID, 'Акция успешно добавлена', reply_markup=to_menu)
            else:
                await bot.send_message(ID,
                                       'Достигнуто максимально колличсетво акций в избранном\nЧто бы удалить акцию нажмите на кнопку ниже',
                                       reply_markup=to_menu)
                logging.info('max size of favourites')
        else:
            await bot.send_message(ID, 'Акция уже в избранном')
            logging.info('stock already in favourites')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
