import random

from pathlib import Path

from src.dataset_utils import get_datasets_path, get_nodes_number, PATH_TO_DATASETS, get_nodes_list, SOURCES, SSBFS, MSBFS

random.seed(42)


def generate_sources(dataset, sources_number):
    nodes = get_nodes_list(dataset)

    return random.sample(nodes, sources_number)


SINGLE_SOURCE_EX_NUMBER = 10


def write_to_file(filepath, text):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(text, encoding='utf-8')


def save_sources(filepath, sources):
    text = ' '.join(map(str, sources))
    write_to_file(filepath, text)


def get_path_for_ss():
    parts = [PATH_TO_DATASETS, SOURCES, SSBFS]
    return Path(*parts)


def get_path_for_ms():
    parts = [PATH_TO_DATASETS, SOURCES, MSBFS]
    return Path(*parts)


def prepare_sources_for_bfs():
    datasets = get_datasets_path()
    for dataset in datasets:
        nodes_number = get_nodes_number(dataset)

        if nodes_number == 0:
            continue

        # single source
        ss_path = get_path_for_ss()
        ss = [generate_sources(dataset, 1)[0] for _ in range(SINGLE_SOURCE_EX_NUMBER)]
        ss_path_parts = [str(ss_path), f"{Path(dataset).stem}.txt"]
        ss_path = Path(*ss_path_parts)
        save_sources(ss_path, ss)

        # multi sources
        ms_path = get_path_for_ms()

        # 10%
        num10per = int(nodes_number * 0.1 + 1)
        ms10 = generate_sources(dataset, num10per)
        ms_path_parts = [str(ms_path), f"{Path(dataset).stem}10.txt"]
        ms_path10 = Path(*ms_path_parts)
        save_sources(ms_path10, ms10)

        # 15%
        num15per = int(nodes_number * 0.15 + 1)
        ms15 = generate_sources(dataset, num15per)
        ms_path_parts = [str(ms_path), f"{Path(dataset).stem}15.txt"]
        ms_path15 = Path(*ms_path_parts)
        save_sources(ms_path15, ms15)

        # 30%
        num30per = int(nodes_number * 0.30 + 1)
        ms30 = generate_sources(dataset, num30per)
        ms_path_parts = [str(ms_path), f"{Path(dataset).stem}30.txt"]
        ms_path30 = Path(*ms_path_parts)
        save_sources(ms_path30, ms30)


if __name__ == "__main__":
    prepare_sources_for_bfs()
