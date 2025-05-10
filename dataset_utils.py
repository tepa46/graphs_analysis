from pathlib import Path

import numpy as np

PATH_TO_DATASETS = "datasets"
SOURCES = 'sources'
SSBFS = 'SSBFS'
MSBFS = 'MSBFS'


def get_datasets_path():
    folder = Path(PATH_TO_DATASETS)
    return [i for i in folder.iterdir() if i.is_file()]


def get_nodes_list(dataset):
    edges = np.loadtxt(dataset, dtype=int, delimiter='\t')

    return list(set((edges[:, 0].tolist() + edges[:, 1].tolist())))


def get_nodes_number(dataset):
    lst = get_nodes_list(dataset)
    return len(lst)


def get_sources_paths_for_bfs_dataset(dataset):
    dataset_path = Path(dataset)
    source_path_parts = [str(dataset_path.parent), SOURCES, SSBFS]
    sources_path = Path(*source_path_parts)

    return [i for i in sources_path.iterdir() if i.stem.startswith(dataset_path.stem)]
