from pyspark.sql import SparkSession

from src.algo.algo import Algo


class SparkPG(Algo):
    def __enter__(self):
        self.spark = (
            SparkSession.builder.appName("pageRank")
            .config("spark.jars.packages", "graphframes:graphframes:0.8.2-spark3.1-s_2.12")
            .getOrCreate()
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.spark.stop()

    def _page_rank(self, edges_rdd, alpha=0.85, eps=1e-8, max_iter=20):
        ranks = edges_rdd.map(lambda x: (x[0], 1.0))

        for i in range(max_iter):
            # print(f"Iteration {i}")
            contrib = (
                edges_rdd.join(ranks)
                .flatMap(lambda x: [(x[1][0], x[1][1] / len(x[1]))])
            )
            new_ranks = (
                contrib.reduceByKey(lambda x, y: x + y)
                .mapValues(lambda rank: (1 - alpha) + alpha * rank)
            )

            diff = ranks.join(new_ranks)
            max_diff = diff.map(lambda x: abs(x[1][0] - x[1][1])).max()
            ranks = new_ranks
            if max_diff < eps:
                break

        return ranks

    def load_data_from_dataset(self, dataset):
        raw_edges = self.spark.read.text(dataset)

        return (
            raw_edges.rdd
            .filter(lambda line: not line.value.startswith("#"))
            .filter(lambda line: len(line.value) > 0)
            .map(lambda line: line.value.split())
            .map(lambda pair: (pair[0], pair[1]))
        )

    def run(self, graph_frame):
        self._page_rank(graph_frame)
        # result_graph.vertices.orderBy(F.desc("pagerank")).show(20)
