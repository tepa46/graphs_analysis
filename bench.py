import timeit

from algo import Algo
from datasets_utils import get_datasets_path


def run_bench(algo: Algo):
    algo_name = type(algo).__name__

    datasets = get_datasets_path()
    for dataset in datasets:
        execution_time = timeit.timeit(lambda: algo.run(dataset), number=20)
        print(f'{algo_name}: {execution_time}\n')

