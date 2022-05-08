import os
import re
from datetime import timedelta

from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.utils import now

TOKEN = 't.BLtZWmlj_Raj-77CQuiflaKQQerwa1MSn56eO_AulW8X2QcC24Bb5RiBF_rjQdzNORfzTEhGmfdJoJeezyu-xQ'
API_TOKEN = '1993104882:AAHEGfoWyrSZaot8l8MMoblgrMaiBPo9cWY'
ID = 802693897
taccount_id = '2097214379'


def main():
    a = []
    with Client(TOKEN) as client:
        operations = client.operations.get_operations(account_id=taccount_id, from_=now() - timedelta(days=30),
                                                      to=now(),
                                                      )
        for oper in operations.operations:
            if only(oper.figi):
                print(oper.figi)
    return 0


def only(string: str) -> bool:
    for let in string:
        if not let in 'ABCDEFGHIGKLMNOPQRSTUVWXYZ1234567890':
            return False
        else:
            return True

if __name__ == "__main__":
    main()
