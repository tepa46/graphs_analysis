from SparkPG import SparkPG
from bench import run_bench

if __name__ == "__main__":
    with SparkPG() as algo:
        run_bench(algo)
