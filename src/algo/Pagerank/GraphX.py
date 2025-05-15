import re

from pyspark.sql import SparkSession
from src.algo.algo import Algo
from graphframes import GraphFrame
from pyspark.sql.types import LongType
from pyspark.sql.types import StructType, StructField


class SparkGraphXPG(Algo):
    def __enter__(self):
        self.spark = SparkSession \
            .builder \
            .appName("PythonPageRank") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .config("spark.jars.packages", "graphframes:graphframes:0.8.2-spark3.1-s_2.12") \
            .getOrCreate()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.spark.stop()

    def load_data_from_dataset(self, dataset):
        lines = self.spark.read.text(str(dataset)).rdd.map(lambda r: r[0])
        return lines.map(parseNeighbors).distinct()

    def run(self, data, additional_data=None, alpha=0.85, eps=1e-6, max_iter=100):
        schema_vertices = StructType([
            StructField("id", LongType(), nullable=False)
        ])

        schema_edges = StructType([
            StructField("src", LongType(), nullable=False),
            StructField("dst", LongType(), nullable=False)
        ])

        vertices = data.flatMap(lambda k: [k[0], k[1]]) \
            .distinct() \
            .map(lambda x: (x,)) \
            .toDF(schema=schema_vertices)

        edges = self.spark.createDataFrame(
            data,
            schema=schema_edges
        )

        graph = GraphFrame(vertices, edges)

        pagerank = graph.pageRank(resetProbability=1 - alpha, tol=eps).vertices

        # print(pagerank.show())
        return


def parseNeighbors(urls: str) -> tuple[int, int]:
    edge_pair = re.split(r'\s+', urls)
    return int(edge_pair[0]), int(edge_pair[1])


def main():
    path = "../../../datasets/Email-Enron.txt"  # Проверьте путь
    with SparkGraphXPG() as algo:
        data = algo.load_data_from_dataset(path)
        algo.run(data)


if __name__ == "__main__":
    main()
