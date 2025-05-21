import re
from operator import add
from typing import Iterable, Tuple

from pyspark.resultiterable import ResultIterable
from pyspark.sql import SparkSession
from src.algo.algo import Algo
from pyspark import StorageLevel


class SparkPG(Algo):
    def __enter__(self):
        self.tmp_path = "/tmp/graph_checkpoints"
        self.spark = (
            SparkSession.builder.appName("PythonPageRank")
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
            .config("spark.cleaner.referenceTracking.cleanCheckpoints", "true")
            .config("spark.driver.memory", "4g")
            .getOrCreate()
        )
        self.spark.sparkContext.setCheckpointDir(self.tmp_path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.spark.stop()

    def load_data_from_dataset(self, dataset):
        lines = self.spark.read.text(str(dataset)).rdd.map(lambda r: r[0])
        links_raw = lines.map(parseNeighbors).distinct()
        all_nodes = links_raw.flatMap(lambda x: [x[0], x[1]]).distinct().cache()

        links = links_raw.groupByKey()
        dangling = all_nodes.subtract(links.keys()).map(lambda n: (n, []))
        full_links = links.union(dangling).persist(StorageLevel.MEMORY_ONLY)

        return full_links

    def run(self, data, additional_data=None, alpha=0.85, eps=1e-6, max_iter=100):
        all_nodes = data.map(lambda k: k[0])
        N = all_nodes.count()
        graph = (
            data.mapValues(lambda x: x if x else [None])
            .partitionBy(200)
            .persist(StorageLevel.MEMORY_ONLY)
        )
        ranks = graph.mapValues(lambda _: 1.0 / N).persist(StorageLevel.MEMORY_ONLY)
        teleport = (1.0 - alpha) / N

        for i in range(max_iter):
            print(i)
            contribs = graph.join(ranks).flatMap(
                lambda x: (
                    [(n, alpha * x[1][1] / len(x[1][0])) for n in x[1][0]]
                    if x[1][0]
                    else []
                )
            )

            total_mass = alpha * (1.0 - ranks.filter(lambda x: x[1]).values().sum())
            dangling_contrib = total_mass / N

            new_ranks = (
                contribs.reduceByKey(add)
                .mapValues(lambda x: x + dangling_contrib + teleport)
                .persist(StorageLevel.MEMORY_ONLY)
            )

            # Проверка сходимости
            delta = ranks.join(new_ranks).map(lambda x: abs(x[1][0] - x[1][1])).sum()
            ranks.unpersist()
            ranks = new_ranks

            ranks.checkpoint()
            if delta < eps:
                break

        return ranks.count()


def computeContribs(
    urls: ResultIterable[str], rank: float
) -> Iterable[Tuple[str, float]]:
    num_urls = len(urls)
    for url in urls:
        yield url, rank / num_urls


def parseNeighbors(urls: str) -> Tuple[str, str]:
    edge_pair = re.split(r"\s+", urls)
    return edge_pair[0], edge_pair[1]


def main():
    path = "../../../datasets/Email-Enron.txt"  # Проверьте путь
    with SparkPG() as algo:
        data = algo.load_data_from_dataset(path)
        algo.run(data)


if __name__ == "__main__":
    main()
