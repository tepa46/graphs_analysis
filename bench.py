import timeit
from pathlib import Path

from algo import Algo
from utils import get_datasets_path

RUN_NUMBER = 20

def run(algo: Algo):
    datasets = get_datasets_path()
    for dataset in datasets:
        dataset_name = Path(dataset).stem
        data = algo.load_data_from_dataset(dataset)

        mean_execution_time = timeit.timeit(lambda: algo.run(data), number=RUN_NUMBER) / RUN_NUMBER

        print(f'{dataset_name}: {1000 * mean_execution_time:.3f} \n')
