import re
from operator import add
from typing import Iterable, Tuple

from pyspark.resultiterable import ResultIterable
from pyspark.sql import SparkSession
from src.algo.algo import Algo
from pyspark.mllib.linalg.distributed import *
import numpy as np


class SparkPG(Algo):
    def __enter__(self):
        self.spark = SparkSession \
            .builder \
            .appName("PythonPageRank") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .getOrCreate()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.spark.stop()

    def load_data_from_dataset(self, dataset):
        lines = self.spark.read.text(dataset).rdd.map(lambda r: r[0])
        links_raw = lines.map(parseNeighbors).distinct()
        all_nodes = links_raw.flatMap(lambda x: [x[0], x[1]]).distinct().cache()

        links = links_raw.groupByKey()
        dangling = all_nodes.subtract(links.keys()).map(lambda n: (n, []))
        full_links = links.union(dangling).cache()

        return full_links

    def run(self, data, additional_data=None, alpha=0.85, eps=1e-8, max_iter=20):
        all_nodes = data.map(lambda k: k[0])
        N = all_nodes.count()
        ranks = all_nodes.map(lambda n: (n, 1.0 / N))
        teleport = (1.0 - alpha) / N

        for i in range(max_iter):
            prev_ranks = ranks

            dangling_mass = (data.filter(lambda x: len(x[1]) == 0).join(ranks).map(lambda n: n[1][1]).sum())
            dangling_share = dangling_mass / N

            contrib = (data.join(ranks).flatMap(lambda nr: computeContribs(nr[1][0], nr[1][1]))).reduceByKey(add)

            ranks = (all_nodes.map(lambda n: (n, None)).leftOuterJoin(contrib).mapValues(
                lambda x: alpha * ((x[1] or 0.0) + dangling_share) + teleport).cache())

            error = ranks.join(prev_ranks).map(lambda x: abs(x[1][0] - x[1][1])).sum()

            if error < eps:
                break

            total = ranks.values().sum()
            print(f"Iteration {i + 1}: error={error:.6e}, dangling_mass={dangling_mass:.6f}, total_rank={total:.6f}")

        for node, rank in ranks.collect():
            print(f"{node}\t{rank:.6f}")


def computeContribs(urls: ResultIterable[str], rank: float) -> Iterable[Tuple[str, float]]:
    num_urls = len(urls)
    for url in urls:
        yield url, rank / num_urls


def parseNeighbors(urls: str) -> Tuple[str, str]:
    edge_pair = re.split(r'\s+', urls)
    return edge_pair[0], edge_pair[1]


def main():
    path = "../../../tmp/Brightkite_edges.txt"  # Проверьте путь
    with SparkPG() as algo:
        data = algo.load_data_from_dataset(path)
        algo.run(data)


if __name__ == "__main__":
    main()
