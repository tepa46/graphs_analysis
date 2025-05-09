from SparkPG import SparkPG
from bench import run_bench

if __name__ == "__main__":
    algo = SparkPG()
    run_bench(algo)
