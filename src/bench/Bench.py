import timeit
import statistics
from pathlib import Path

from src.algo.algo import Algo
from src.dataset_utils import get_datasets_path

RUN_NUMBER = 20


class Bench:
    # Collects a list of additional data with which the algorithm will be run on the dataset.
    #
    # List element has a format (addition_data_presentable_name, addition_data).
    # `addition_data_presentable_name` uses for bench results displaying.
    #
    # NOTE! Algorithm will be run with each additional data separately.
    # NOTE! Returns [('', None)] if no additional data is required to run algorithm.
    def collect_additional_data_lst(self, dataset) -> list:
        pass

    def _run_bench(self, algo: Algo, data, additional_data=None):
        times = [
            timeit.timeit(lambda: algo.run(data, additional_data), number=1)
            for _ in range(RUN_NUMBER)
        ]

        return statistics.mean(times), statistics.stdev(times)

    def run_bench(self, algo: Algo):
        datasets = get_datasets_path()
        for dataset in datasets:
            dataset_name = Path(dataset).stem
            data = algo.load_data_from_dataset(dataset)

            additional_data_lst = self.collect_additional_data_lst(dataset)

            for (addition_data_name, addition_data) in additional_data_lst:
                mean_exec_time, std_time = self._run_bench(algo, data, addition_data)
                print(f'{dataset_name} {addition_data_name}: {1000 * mean_exec_time:.3f} {1000 * std_time:.3f}')
