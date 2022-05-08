from tinkoff.invest import Client, InstrumentIdType

TOKEN = 't.BLtZWmlj_Raj-77CQuiflaKQQerwa1MSn56eO_AulW8X2QcC24Bb5RiBF_rjQdzNORfzTEhGmfdJoJeezyu-xQ'
from typing import List


def get_stocks() -> List:
    stocks_spb = []
    stocks_moex = []
    with Client(TOKEN) as client:
        stocks = client.instruments.shares().instruments
        for stock in stocks:
            if stock.exchange == 'SPB':
                stocks_spb.append(stock.figi)
            elif stock.exchange == 'MOEX':
                stocks_moex.append(stock.figi)

