import getopt
import subprocess
import sys

from typing import Any, List
from hyperopt_manager.get_pickle_data import get_pickle_data
from hyperopt_manager.database_manager import create_database, insert_table_data
from tests.conftest import get_args


# TODO Export --spaces params detection and logic into separate module

def hyperopt_manager_start(argv: Any) -> None:
    """
    Manages the freqtrade hyperopt command with its parameters (--cmd or -x). \n
    Determines how often the hyperopt command should run (--iterations or -y). \n
    Creates a SQLite DB (--drop_db_file or -z) according to parameters after --spaces. Therefore it is necessary that
    --spaces is the last parameter in your freqtrade hyperopt command. \n
    If you change the parameters for --spaces, please set --drop_db_file to true

    Args:
        argv: Commandline arguments. Type 'python hyperopt_manager_start.py -h' for more info

    Returns:
        None: Nothing
    """
    freqtrade_cmd = None
    table_params = None
    iterations = None
    db_bool = None

    try:
        opts, args = getopt.getopt(argv, 'hx:y:z:', ['cmd=', 'iterations=', 'drop_db_file='])
    except getopt.GetoptError as err:
        print('hyperopt_manager.py --cmd <str> --iterations <int> --drop_db_file <bool>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('hyperopt_manager.py --cmd <str> --iterations <int> --drop_db_file <bool>')
            sys.exit()
        if opt in ('--cmd', '-x'):
            freqtrade_cmd = arg
            hyperopt_params_list = list(arg.split(' '))
            spaces_index = hyperopt_params_list.index('--spaces')
            table_params = hyperopt_params_list[(spaces_index + 1):]
        if opt in ('--iterations', '-y'):
            iterations = int(arg)
        if opt in ('--drop_db_file', '-z'):
            if arg.lower() == 'true':
                db_bool = True
            else:
                db_bool = False

    if db_bool:
        create_database('hyperopt_manager/hyperopt.results.sqlite', table_params)

    hypermanager_workload(freqtrade_cmd, iterations, table_params)


def hypermanager_workload(freqtrade_cmd: str, iterations: int, table_data: List) -> None:
    """
    Runs the freqtrade hyperopt command, saves the epoch data of the current run and insert it into the
    SQLite DB.

    Args:
        freqtrade_cmd: Freqtrade hyperopt command.
        iterations: How often to run the hyperopt command.
        table_data: --spaces parameter.

    Returns:
        None: Nothing
    """
    hl_args = ['hyperopt-list']
    hl_pargs = get_args(hl_args)

    if 'all' in table_data:
        table_data = ['buy', 'sell', 'roi', 'stoploss', 'trailing']
    elif 'default' in table_data:
        table_data = ['buy', 'sell', 'roi', 'stoploss']

    for i in range(0, iterations):
        insert_strut = [[], []]
        insert_strut[0] = table_data

        subprocess.call(freqtrade_cmd, shell=True)

        raw_data = get_pickle_data(hl_pargs)

        for epoch in range(0, raw_data[1]):
            # [iteration, best_local_min, current_epoch, trades_count, avg_profit_pct, total_profit_currency,
            #  total_profit_pct, avg_duration_minutes, loss_func, SPACES PARAMS]
            tmp = [
                i,
                raw_data[0][epoch]['is_best'],
                raw_data[0][epoch]['current_epoch'],
                raw_data[0][epoch]['results_metrics']['trade_count'],
                raw_data[0][epoch]['results_metrics']['avg_profit'],
                raw_data[0][epoch]['results_metrics']['total_profit'],
                raw_data[0][epoch]['results_metrics']['profit'],
                raw_data[0][epoch]['results_metrics']['duration'],
                raw_data[0][epoch]['loss']
            ]

            for param in insert_strut[0]:
                tmp.append(raw_data[0][epoch]['params_details'][param])

            insert_strut[1].append(tmp)

        insert_table_data('hyperopt_manager/hyperopt.results.sqlite', insert_strut)


if __name__ == "__main__":
    hyperopt_manager_start(sys.argv[1:])
