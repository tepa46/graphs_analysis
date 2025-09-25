from src.algo.Pagerank.PysparkSql import SparkSQLPagerank
from src.bench.PageRank.PageRankBench import PageRankBench

if __name__ == "__main__":
    with SparkSQLPagerank() as algo:
        PageRankBench().run_bench(algo)
