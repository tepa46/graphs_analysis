from pathlib import Path

import numpy as np

PATH_TO_DATASETS = "../datasets"
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


def get_sources_paths_for_bfs_dataset(all_sources_paths, dataset_name):
    return [i for i in all_sources_paths.iterdir() if i.stem.startswith(dataset_name)]


def get_sources_paths_for_ssbfs_dataset(dataset):
    dataset_path = Path(dataset)
    source_path_parts = [str(dataset_path.parent), SOURCES, SSBFS]

    return get_sources_paths_for_bfs_dataset(Path(*source_path_parts), dataset_path.stem)


def get_sources_paths_for_msbfs_dataset(dataset):
    dataset_path = Path(dataset)
    source_path_parts = [str(dataset_path.parent), SOURCES, MSBFS]

    a = get_sources_paths_for_bfs_dataset(Path(*source_path_parts), dataset_path.stem)
    return a

