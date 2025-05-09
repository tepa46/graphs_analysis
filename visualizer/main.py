from os import path, listdir
import os
from collections import defaultdict
import matplotlib.pyplot as plt

RESULT_DIR_PATH = "../output"


# ["Algo"]["Realization"]["dataset"]


def read_benchmark(datasetPath):
    return {k: float(v) for line in open(datasetPath) for k, v in [line.strip().split(': ')]}


class Visualizer:
    def __init__(self):
        results = defaultdict(dict)
        for algo in get_algo_name():
            for realization, full_path in get_realization_name(algo):
                results[algo][realization] = read_benchmark(full_path)

        self.bench = results

    def single_algo_plot(self, algoName, realizationName):
        if algoName not in self.bench:
            return

        if realizationName not in self.bench[algoName]:
            return

        print("OK")

    def all_algo_realizations_compare_plot(self, algoName):
        if algoName not in self.bench:
            return

        if len(self.bench[algoName]) == 0:
            return

        print("OK")

def get_algo_name():
    return [i for i in listdir(RESULT_DIR_PATH) if path.isdir(path.join(RESULT_DIR_PATH, i))]


def get_realization_name(algoName):
    r = path.join(RESULT_DIR_PATH, algoName)
    return [(path.splitext(i)[0], path.join(r, i)) for i in listdir(r)]


def main():
    v = Visualizer()
    print(v.bench)
    v.single_algo_plot("Pagerank", "spark")
    # print(get_realization_name("Pagerank"))


if __name__ == '__main__':
    main()
