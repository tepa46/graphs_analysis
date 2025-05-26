import linecache
import random

from pathlib import Path

from src.dataset_utils import (
    get_datasets_path,
    PATH_TO_DATASETS,
    SOURCES,
    SSBFS,
    MSBFS,
)

random.seed(42)


def count_lines(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return sum(1 for _ in f)


def generate_sources(file_path, num_samples):
    file_path = str(file_path)
    total_lines = count_lines(file_path)
    samples = random.sample(
        range(1, total_lines + 1), min(num_samples * 2, total_lines)
    )
    nodes = set()

    for i in samples:
        line = linecache.getline(file_path, i)
        if line:
            parts = line.strip().split()
            if len(parts) == 2:
                nodes.update(parts)
            if len(nodes) >= num_samples:
                break

    return random.sample(list(nodes), num_samples)


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

        print(f"Generated sources for {Path(dataset).stem}")


if __name__ == "__main__":
    prepare_sources_for_bfs()
