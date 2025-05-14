from pyspark.sql import SparkSession
from pyspark import StorageLevel
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType
import shutil


class SparkSSBFS:
    def __enter__(self):
        self.tmp_path = "/tmp/graph_checkpoints"
        self.spark = SparkSession.builder \
            .appName("SS-BFS") \
            .master("local[*]") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .config("spark.cleaner.referenceTracking.cleanCheckpoints", "true") \
            .config("spark.memory.offHeap.enabled", "true") \
            .config("spark.driver.memory", "4g") \
            .config("spark.executor.memory", "4g") \
            .config("spark.memory.offHeap.size", "4g") \
            .getOrCreate()
        self.spark.sparkContext.setCheckpointDir(self.tmp_path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.spark.stop()

    def load_data_from_dataset(self, dataset):
        df = self.spark.read.text(str(dataset)) \
            .select(F.split(F.col("value"), r"\s+").alias("cols")) \
            .filter(F.size("cols") == 2) \
            .select(
            F.col("cols").getItem(0).cast("long").alias("src"),
            F.col("cols").getItem(1).cast("long").alias("dst")
        )

        rev = df.select(F.col("dst").alias("src"), F.col("src").alias("dst"))
        edges = df.union(rev).distinct() \
            .repartition(200, "src") \
            .persist(StorageLevel.MEMORY_AND_DISK)
        return edges

    def run(self, data, additional_data=None):
        if additional_data is None:
            print("No start vertex input")
            return

        schema = StructType([
            StructField("vertex", LongType(), nullable=False),
            StructField("src", LongType(), nullable=False),
            StructField("dist", IntegerType(), nullable=False),
            StructField("parent", LongType(), nullable=True)
        ])

        tmp = [(int(additional_data), int(additional_data), 0, int(additional_data))]
        init = self.spark.createDataFrame(tmp, schema=schema)
        front = init.persist(StorageLevel.MEMORY_AND_DISK)
        visited = init.persist(StorageLevel.MEMORY_AND_DISK)

        front = front.checkpoint()
        visited = visited.checkpoint()

        while True:
            neighbors = front.alias("f") \
                .join(data.alias("e"), F.col("f.vertex") == F.col("e.src")) \
                .select(
                F.col("e.dst").alias("vertex"),
                F.col("f.src"),
                (F.col("f.dist") + 1).alias("dist"),
                F.col("f.vertex").alias("parent")
            )

            new_front = neighbors.join(
                visited.select("vertex", "src"),
                on=["vertex", "src"],
                how="left_anti"
            ).persist(StorageLevel.MEMORY_AND_DISK)

            if new_front.limit(1).count() == 0:
                break

            visited.unpersist()
            visited = visited.union(new_front).persist(StorageLevel.MEMORY_AND_DISK)

            front.unpersist()
            front = new_front

            front = front.checkpoint()
            visited = visited.checkpoint()

        # visited.limit(10).show()
        print("ОДИН РАЗ ПОСЧИТАЛ")
        visited.unpersist()
        front.unpersist()

        shutil.rmtree(self.tmp_path)

        return visited


def main():
    path = "../../../tmp/Brightkite_edges.txt"  # Проверьте путь
    with SparkSSBFS() as algo:
        data = algo.load_data_from_dataset(path)
        algo.run(data, additional_data=41905)


if __name__ == "__main__":
    main()
