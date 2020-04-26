from freqtrade.configuration import setup_utils_configuration
from freqtrade.state import RunMode
from typing import Any, Dict, List, Union
from freqtrade.optimize.hyperopt import Hyperopt


def get_pickle_data(args: Dict[str, Any]) -> List[Union[List, int]]:
    """
    Fetches the pickle file and returns its raw data.

    Returns:
        List[List[], int]: pickle data, total epochs
    """
    config = setup_utils_configuration(args, RunMode.UTIL_NO_EXCHANGE)

    trials_file = (config['user_data_dir'] /
                   'hyperopt_results' / 'hyperopt_results.pickle')

    # Previous evaluations
    trials = Hyperopt.load_previous_results(trials_file)
    total_epochs = len(trials)

    return [trials, total_epochs]
