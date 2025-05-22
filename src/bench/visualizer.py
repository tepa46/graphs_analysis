from os import path, listdir
import os
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

BENCHMARKS_DIR_PATH = "../../out/benchmarks"
PLOT_DIRNAME = "../../out/graphs"


class Visualizer:
    def __init__(self):
        results = defaultdict(dict)
        for algo in get_algo_name():
            for realization, full_path in get_realization_name(algo):
                print(full_path)
                results[algo][realization] = read_benchmark(full_path)

        self.save_dir = PLOT_DIRNAME
        os.makedirs(self.save_dir, exist_ok=True)

        self.bench = results

    def _save_plot(self, name):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
        filename = f"plot_{name}_{timestamp}.png"
        plt.savefig(path.join(self.save_dir, filename), dpi=300)

    def single_algo_plot(self, algoName, realizationName):
        if algoName not in self.bench:
            print(f"Algo {algoName} not found")
            return

        if realizationName not in self.bench[algoName]:
            print(f"Realization {realizationName} not found")
            return

        x = self.bench[algoName][realizationName].keys()
        y = [v[0] for v in self.bench[algoName][realizationName].values()]
        err = [v[1] for v in self.bench[algoName][realizationName].values()]

        title = f"{algoName} with {realizationName}"

        x_label = "Dataset"
        y_label = "Time (ms)"

        plt.grid(axis="y", linestyle="--", alpha=0.5, zorder=1)
        plt.bar(x, y, zorder=2, edgecolor="black", width=0.5, yerr=err, capsize=3)
        plt.yscale("log")
        plt.title(title)
        plt.xlabel(x_label)

        plt.text(
            0.05,
            1.02,
            y_label,
            transform=plt.gca().transAxes,
            rotation=0,
            ha="right",
            va="bottom",
        )

        self._save_plot(f"{algoName}_{realizationName}")
        clean_plot()

    def all_algo_realizations_compare_plot(self, algoName):
        if algoName not in self.bench:
            print(f"Algo {algoName} not found")
            return

        if len(self.bench[algoName]) == 0:
            print(f"No realizations for algo {algoName}")
            return

        data, datasets_name = defaultdict(), set()
        realizationNames = list(self.bench[algoName].keys())

        for r in realizationNames:
            for k, v in self.bench[algoName][r].items():
                datasets_name.add(k)
                data.setdefault(r, []).append(v[0])

        x = np.arange(len(datasets_name))
        width = 0.25
        multiplier = 0

        fig, ax = plt.subplots(layout="constrained", figsize=(10, 6))

        for spine in ax.spines.values():
            spine.set_visible(False)

        for attribute, measurement in data.items():
            offset = width * multiplier
            ax.bar(
                x + offset,
                measurement,
                width,
                label=attribute,
                zorder=2,
                edgecolor="black",
                capsize=3,
            )
            multiplier += 1

        y_label = "Time (ms)"
        ax.text(
            0.05,
            1.02,
            y_label,
            transform=plt.gca().transAxes,
            rotation=0,
            ha="right",
            va="bottom",
        )

        ax.set_xticks(x + width, datasets_name)
        ax.grid(axis="y", linestyle="--", alpha=0.5, zorder=1)
        ax.set_yscale("log")
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, 1.1),
            ncol=len(datasets_name),
            frameon=False,
        )
        plt.tight_layout(pad=3.0)
        self._save_plot(f"{algoName}_compareAll")
        clean_plot(fig)


def clean_plot(fig=None):
    plt.cla()
    plt.clf()
    plt.close()
    if fig is not None:
        plt.close(fig)


def read_benchmark(datasetPath):
    result = {}
    with open(datasetPath) as f:
        for line in f:
            k, rest = line.strip().split(": ")
            mean, std = map(float, rest.split())
            result[k] = (mean, std)
    return result



def get_algo_name():
    return [
        i
        for i in listdir(BENCHMARKS_DIR_PATH)
        if path.isdir(path.join(BENCHMARKS_DIR_PATH, i))
    ]


def get_realization_name(algoName):
    r = path.join(BENCHMARKS_DIR_PATH, algoName)
    return [(path.splitext(i)[0], path.join(r, i)) for i in listdir(r)]


def main():
    v = Visualizer()
    for i in ["Pagerank", "SSBFS", "MSBFS16", "MSBFS32", "MSBFS64"]:
        v.all_algo_realizations_compare_plot(i)
        for j in ["Gunrock", "GraphBLAS"]:
            v.single_algo_plot(i, j)


if __name__ == "__main__":
    main()
