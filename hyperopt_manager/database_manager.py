import os
import sqlite3

from typing import List
from colorama import Fore


def create_database(db_file: str, table_data: List) -> None:
    """
    Creates a SQLite DB file and a table to hold all relevant hyperopt data from each epoch in each iteration.

    Args:
        db_file: Path to the SQLite DB file
        table_data: Spaces parameter from the freqtrade hyperopt command

    Returns:
        None: Nothing
    """
    connection = None
    add_col = []

    table_root = '''id INTEGER PRIMARY KEY,
                    iteration INTEGER NOT NULL,
                    best_local_min TEXT NOT NULL,
                    current_epoch INTEGER NOT NULL,
                    trades_count INTEGER NOT NULL,
                    avg_profit_pct REAL NOT NULL,
                    total_profit_currency REAL NOT NULL,
                    total_profit_pct REAL NOT NULL,
                    avg_duration_minutes REAL NOT NULL,
                    loss_func REAL NOT NULL, '''

    spaces_col = {'buy': 'buy TEXT NOT NULL',
                  'sell': 'sell TEXT NOT NULL',
                  'roi': 'roi TEXT NOT NULL',
                  'stoploss': 'stoploss TEXT NOT NULL',
                  'trailing': 'trailing TEXT NOT NULL'}

    try:
        os.remove(db_file)
    except OSError as err:
        print(err)

    try:
        connection = sqlite3.connect(db_file)
        cursor = connection.cursor()
        print(f"{Fore.MAGENTA}Successfully connected to SQLite DB - {db_file}{Fore.RESET}")

        if 'all' in table_data:
            table_data = ['buy', 'sell', 'roi', 'stoploss', 'trailing']
        elif 'default' in table_data:
            table_data = ['buy', 'sell', 'roi', 'stoploss']

        for param in table_data:
            add_col.append(spaces_col[param])

        table_root += ', '.join(add_col)

        create_hyperopt_data_table = 'CREATE TABLE hyperopt_results (' + table_root + ');'

        cursor.execute(create_hyperopt_data_table)
        connection.commit()
        print(f'{Fore.MAGENTA}Table successfully created.{Fore.RESET}')

        cursor.close()
    except sqlite3.Error as err:
        print(err)
    finally:
        if connection:
            connection.close()
            print(f'{Fore.MAGENTA}The SQLite connection is closed{Fore.RESET}')


def insert_table_data(db_file: str, insert_data: List) -> None:
    """
    Inserts the epoch data of one freqtrade hyperopt command iteration one by one.

    Args:
        db_file: SQLite DB file to insert data into
        insert_data: Epoch data from one run as a batch

    Returns:
        None: Nothing
    """
    connection = None

    table_root = 'iteration, best_local_min, current_epoch, trades_count, avg_profit_pct, total_profit_currency,' \
                 'total_profit_pct, avg_duration_minutes, loss_func, '

    try:
        connection = sqlite3.connect(db_file)
        cursor = connection.cursor()

        table_root += ', '.join(insert_data[0])

        for entry in insert_data[1]:
            insert_hyperopt_results = 'INSERT INTO hyperopt_results (' + table_root + ') ' \
                                      'VALUES ("' + '", "'.join(str(x) for x in entry) + '");'
            cursor.execute(insert_hyperopt_results)

        connection.commit()
        print(f'{Fore.MAGENTA}Records successfully inserted.{Fore.RESET}')

        cursor.close()
    except sqlite3.Error as err:
        print(err)
    finally:
        if connection:
            connection.close()
            print(f'{Fore.MAGENTA}The SQLite connection is closed{Fore.RESET}')
