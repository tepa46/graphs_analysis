from os import path, listdir
import os
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

BENCHMARKS_DIR_PATH = "../../out/benchmarks"
PLOT_DIRNAME = "../../out/graphs"
BFS_ALGOS = ["SSBFS", "MSBFS16", "MSBFS32", "MSBFS64"]

BFS_COMP = "BFSComp"
GRAPHBLAS_COMP = "GraphBLASBFSComp.txt"
GUNROCK_COMP = "GunrockBFSComp.txt"


class Visualizer:
    def __init__(self):
        results = defaultdict(dict)
        for algo in get_algo_name():
            for realization, full_path in get_realization_name(algo):
                print(full_path)
                results[algo][realization] = read_benchmark(full_path)

        full_path = path.join(BENCHMARKS_DIR_PATH, GRAPHBLAS_COMP)
        results[BFS_COMP]["GraphBLAS"] = read_bfs_comp_benchmark(full_path)
        full_path = path.join(BENCHMARKS_DIR_PATH, GUNROCK_COMP)
        results[BFS_COMP]["Gunrock"] = read_bfs_comp_benchmark(full_path)

        self.save_dir = PLOT_DIRNAME
        os.makedirs(self.save_dir, exist_ok=True)

        self.bench = results

    def _save_plot(self, name):
        filename = f"{name}.png"
        plt.savefig(path.join(self.save_dir, filename), dpi=300)

    def plot_bfs_comparisons_per_realization2(self):
        os.makedirs(self.save_dir, exist_ok=True)
        bfs_comp_bench = self.bench[BFS_COMP]
        all_impls = list(bfs_comp_bench.keys())

        all_datasets = sorted(
            {dataset for impl in bfs_comp_bench for dataset in bfs_comp_bench[impl]}
        )

        for impl in all_impls:
            bfs_com_bench_for_impl = bfs_comp_bench[impl]
            ratios = {
                alg: [float(bfs_com_bench_for_impl[g][i]) for g in all_datasets]
                for i, alg in enumerate(BFS_ALGOS)
            }

            x = np.arange(len(all_datasets))
            width = 0.2

            fig, ax = plt.subplots(figsize=(12, 6))

            for idx, alg in enumerate(BFS_ALGOS):
                ax.scatter(x, ratios[alg], marker="o", label=alg)

            ax.axhline(
                1.0,
                color="gray",
                linestyle="--",
                linewidth=1,
                label="Baseline (SSBFS = 1)",
            )
            # ax.set_ylim(bottom=0)
            # yticks = list(ax.get_yticks())
            # if 1.0 not in yticks:
            #     yticks.append(1.0)
            #     yticks = sorted(yticks)
            #     ax.set_yticks(yticks)

            ax.set_xticks(x)
            ax.set_xticklabels(all_datasets, rotation=45, ha="right")
            ax.set_xlabel("Graph")
            ax.set_ylabel("Time Ratio")
            ax.set_title(f"{impl} BFS Algorithms Time Ratios Across Graphs")
            ax.grid(True, linestyle="--", alpha=0.5)
            ax.legend(title="Algorithm", bbox_to_anchor=(1.05, 1), loc="upper left")
            plt.tight_layout()

            out_path = os.path.join(
                self.save_dir, f"{impl.lower()}_bfs_comparison2.png"
            )
            plt.savefig(out_path, dpi=300)
            plt.close()

    def plot_bfs_comparisons_per_realization(self):
        os.makedirs(self.save_dir, exist_ok=True)
        bfs_bench = {
            algo: realization
            for algo, realization in self.bench.items()
            if algo in BFS_ALGOS
        }

        all_realizations = sorted(
            {realization for algo in bfs_bench for realization in bfs_bench[algo]}
        )

        all_datasets = sorted(
            {
                dataset
                for algo in bfs_bench
                for realization in bfs_bench[algo]
                for dataset in bfs_bench[algo][realization]
            }
        )

        for realization in all_realizations:
            x = np.arange(len(all_datasets))
            bar_width = 0.8 / len(bfs_bench)

            plt.figure(figsize=(14, 7))

            for idx, algo in enumerate(sorted(bfs_bench.keys())):
                means = []
                stds = []
                for dataset in all_datasets:
                    if (
                        realization in bfs_bench[algo]
                        and dataset in bfs_bench[algo][realization]
                    ):
                        mean, std = bfs_bench[algo][realization][dataset]
                        means.append(mean)
                        stds.append(std)
                    else:
                        means.append(0)
                        stds.append(0)
                plt.bar(
                    x + (idx - len(bfs_bench) / 2) * bar_width + bar_width / 2,
                    means,
                    width=bar_width,
                    yerr=stds,
                    capsize=5,
                    label=algo,
                )

            plt.xlabel("Dataset")
            plt.ylabel("Time (ms, log scale)")
            plt.title(f"BFS Comparison: {realization}")
            plt.xticks(x, all_datasets, rotation=30)
            plt.yscale("log")
            plt.legend(title="Algo")
            plt.grid(axis="y", linestyle="--", alpha=0.7)
            plt.tight_layout()

            out_path = os.path.join(
                self.save_dir, f"{realization.lower()}_bfs_comparison.png"
            )
            plt.savefig(out_path, dpi=300)
            plt.close()

    def all_algo_realizations_compare_plot(self, algoName):
        if algoName not in self.bench:
            print(f"Algo {algoName} not found")
            return

        if len(self.bench[algoName]) == 0:
            print(f"No realizations for algo {algoName}")
            return

        data_means = defaultdict(list)
        data_stds = defaultdict(list)
        datasets_name = set()
        realizationNames = list(self.bench[algoName].keys())

        for r in realizationNames:
            for k, v in self.bench[algoName][r].items():
                datasets_name.add(k)
                data_means[r].append(v[0])
                data_stds[r].append(v[1])

        datasets_name = sorted(datasets_name)
        x = np.arange(len(datasets_name))
        width = 0.8 / len(realizationNames)
        multiplier = 0

        fig, ax = plt.subplots(layout="constrained", figsize=(10, 6))

        for spine in ax.spines.values():
            spine.set_visible(False)

        for realization in realizationNames:
            offset = width * multiplier
            means = data_means[realization]
            stds = data_stds[realization]

            ax.bar(
                x + offset,
                means,
                width,
                label=realization,
                zorder=2,
                edgecolor="black",
                yerr=stds,
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

        ax.set_xticks(x + width * (len(realizationNames) - 1) / 2)
        ax.set_xticklabels(datasets_name)
        ax.grid(axis="y", linestyle="--", alpha=0.5, zorder=1)
        ax.set_yscale("log")
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, 1.1),
            ncol=len(realizationNames),
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


def read_bfs_comp_benchmark(dataset_path):
    result = {}
    with open(dataset_path) as f:
        for line in f:
            k, rest = line.strip().split(": ")
            r1, r2, r3, r4 = rest.split()
            result[k] = (r1, r2, r3, r4)
    return result


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


def create_all_possible_graphs():
    v = Visualizer()
    for i in ["Pagerank", "SSBFS", "MSBFS16", "MSBFS32", "MSBFS64"]:
        v.all_algo_realizations_compare_plot(i)
        for j in ["Gunrock", "GraphBLAS"]:
            v.single_algo_plot(i, j)
    v.plot_bfs_comparisons_per_realization()
    v.plot_bfs_comparisons_per_realization2()


if __name__ == "__main__":
    create_all_possible_graphs()
