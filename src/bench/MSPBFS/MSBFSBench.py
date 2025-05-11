from pathlib import Path

import numpy as np

from src.bench.Bench import Bench
from src.dataset_utils import get_sources_paths_for_msbfs_dataset


class MSBFSBench(Bench):
    def collect_additional_data_lst(self, dataset) -> list:
        additional_data_lst = list()

        source_paths = get_sources_paths_for_msbfs_dataset(dataset)
        for source_path in source_paths:
            source_path_name = Path(source_path).stem
            sources = np.loadtxt(source_path, dtype=int, delimiter=' ')
            additional_data_lst.append((source_path_name, sources))

        return additional_data_lst
