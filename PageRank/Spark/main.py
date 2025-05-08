from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from graphframes import GraphFrame
from os import listdir, path

PATH_TO_DATASETS = "../../datasets"


def get_datasets_path():
    return [path.join(PATH_TO_DATASETS, i) for i in listdir(PATH_TO_DATASETS)]


def main():
    datasets = get_datasets_path()
    p = datasets[0]
    print(p)
    spark = (
        SparkSession.builder.appName("SNAPPageRank")
        .config("spark.jars.packages", "graphframes:graphframes:0.8.2-spark3.1-s_2.12")
        .getOrCreate()
    )

    raw_edges = spark.read.text(p)
    print(raw_edges.show(10))


if __name__ == "__main__":
    main()
