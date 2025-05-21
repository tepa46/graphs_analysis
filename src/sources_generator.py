import random

from pathlib import Path

from src.dataset_utils import (
    get_datasets_path,
    get_nodes_number,
    PATH_TO_DATASETS,
    get_nodes_list,
    SOURCES,
    SSBFS,
    MSBFS,
)

random.seed(42)


def generate_sources(dataset, sources_number):
    nodes = get_nodes_list(dataset)

    return random.sample(nodes, min(len(nodes), sources_number))


SINGLE_SOURCE_EX_NUMBER = 10


def write_to_file(filepath, text):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(text, encoding="utf-8")


def save_sources(filepath, sources):
    text = " ".join(map(str, sources))
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

        # 16
        ms16 = generate_sources(dataset, 16)
        ms_path_parts = [str(ms_path), f"{Path(dataset).stem}16.txt"]
        ms_path16 = Path(*ms_path_parts)
        save_sources(ms_path16, ms16)

        # 32
        ms32 = generate_sources(dataset, 32)
        ms_path_parts = [str(ms_path), f"{Path(dataset).stem}32.txt"]
        ms_path32 = Path(*ms_path_parts)
        save_sources(ms_path32, ms32)

        # 64
        ms64 = generate_sources(dataset, 64)
        ms_path_parts = [str(ms_path), f"{Path(dataset).stem}64.txt"]
        ms_path64 = Path(*ms_path_parts)
        save_sources(ms_path64, ms64)


if __name__ == "__main__":
    prepare_sources_for_bfs()
