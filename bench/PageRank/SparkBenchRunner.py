from bench.PageRank.PageRankBench import PageRankBench
from pageRank.Spark.SparkPG import SparkPG

if __name__ == "__main__":
    with SparkPG() as algo:
        PageRankBench().run_bench(algo)
