import numpy as np

from src.bench.Bench import Bench
from src.dataset_utils import get_sources_paths_for_bfs_dataset


class SSBFSBench(Bench):
    def collect_additional_data_lst(self, dataset) -> list:
        source_paths = get_sources_paths_for_bfs_dataset(dataset)
        sources = np.loadtxt(source_paths[0], dtype=int, delimiter=' ').tolist()

        return [(str(source), source) for source in sources]
