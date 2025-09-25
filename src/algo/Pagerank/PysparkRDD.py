import re
from typing import Optional, Tuple, Dict

from src.algo.algo import Algo

from pyspark.sql import SparkSession
from pyspark import StorageLevel
import numpy as np


class SparkRDD(Algo):
    def __enter__(self):
        self.tmp_path = "/tmp/graph_checkpoints"
        self.spark = (
            SparkSession.builder.appName("PageRankBroadcast")
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
            .config("spark.driver.memory", "4g")
            .config("spark.executor.memory", "2g")
            .config("spark.executor.cores", "4")
            .config("spark.executor.instances", "2")
            .config("spark.eventLog.enabled", "true")
            .config(
                "spark.eventLog.dir",
                "/home/pavlusha/Documents/Spbu/graphs_analysis/logs",
            )
            .getOrCreate()
        )
        self.sc = self.spark.sparkContext
        self.sc.setCheckpointDir(self.tmp_path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.spark.stop()

    def load_data_from_dataset(self, dataset: str):
        print("Loading data from dataset", dataset)
        lines = self.spark.read.text(str(dataset)).rdd.map(lambda r: r[0])
        edges = lines.map(lambda line: parseNeighbors(line)).filter(
            lambda x: x is not None
        )
        links = edges.distinct()

        all_nodes = links.flatMap(lambda x: [x[0], x[1]]).distinct()
        out_links = links.groupByKey().mapValues(lambda it: list(it))
        dangling = all_nodes.subtract(out_links.keys()).map(lambda n: (n, []))
        adjacency = out_links.union(dangling).persist(StorageLevel.MEMORY_AND_DISK)
        adjacency.count()
        return adjacency

    def run(
        self,
        adjacency,
        additional_data=None,
        alpha=0.85,
        eps=1e-6,
        max_iter=100,
        checkpoint_every=20,
    ):
        nodes_rdd = (
            adjacency.keys()
            .distinct()
            .zipWithIndex()
            .persist(StorageLevel.MEMORY_AND_DISK)
        )
        nodes_rdd.count()
        indexmap: Dict[str, int] = dict(nodes_rdd.collect())  #
        N = len(indexmap)
        if N == 0:
            return np.array([])

        def make_triplets(record):
            src, nbrs = record
            src_idx = indexmap[src]
            if not nbrs:
                return []
            prob = 1.0 / len(nbrs)
            out = []
            for n in nbrs:
                nid = indexmap.get(n)
                if nid is not None:
                    out.append((src_idx, (nid, prob)))
            return out

        hashed_matrix = adjacency.flatMap(make_triplets).persist(
            StorageLevel.MEMORY_ONLY
        )
        hashed_matrix.count()

        dangling_idxs = (
            adjacency.filter(lambda x: len(x[1]) == 0)
            .keys()
            .map(lambda n: indexmap[n])
            .collect()
        )
        dangling_idxs = np.array(dangling_idxs, dtype=int)

        pgrnk = np.full(N, 1.0 / N, dtype=float)
        teleport = (1.0 - alpha) / N

        for it in range(1, max_iter + 1):
            bcast_ranks = self.sc.broadcast(pgrnk)
            contribs = hashed_matrix.map(
                lambda x: (x[1][0], alpha * bcast_ranks.value[x[0]] * x[1][1])
            )

            summed = contribs.reduceByKey(lambda a, b: a + b)

            contrib_items = summed.collect()  # list[(idx, float)]
            new_r = np.zeros(N, dtype=float)
            if contrib_items:
                indices = np.fromiter(
                    (i for i, _ in contrib_items), dtype=int, count=len(contrib_items)
                )
                values = np.fromiter(
                    (v for _, v in contrib_items), dtype=float, count=len(contrib_items)
                )
                new_r[indices] = values

            if dangling_idxs.size > 0:
                dangling_mass = alpha * pgrnk[dangling_idxs].sum()
            else:
                dangling_mass = 0.0

            new_r += dangling_mass / N + teleport

            delta = np.abs(new_r - pgrnk).sum()
            pgrnk = new_r

            try:
                bcast_ranks.destroy()
            except Exception:
                try:
                    bcast_ranks.unpersist()
                except Exception:
                    pass

            if it % checkpoint_every == 0:
                try:
                    hashed_matrix.checkpoint()
                    hashed_matrix.count()
                except Exception:
                    pass

            if delta < eps:
                print("Converged.")
                break

        return pgrnk


def parseNeighbors(urls: str) -> Optional[Tuple[str, str]]:
    if urls is None:
        return None
    s = urls.strip()
    if not s or s.startswith("#"):
        return None
    parts = re.split(r"\s+", s)
    if len(parts) < 2:
        return None
    return parts[0], parts[1]


def main():
    path = "/home/pavlusha/Documents/Spbu/graphs_analysis/tmp/Wiki-Vote.txt"  # Проверьте путь
    with SparkRDD() as algo:
        data = algo.load_data_from_dataset(path)
        ranks = algo.run(data)
        if isinstance(ranks, np.ndarray):
            topk = np.argsort(-ranks)[:10]
            print("Top 10 indices (by rank):", topk)
            print("Top 10 ranks:", ranks[topk])


if __name__ == "__main__":
    main()
