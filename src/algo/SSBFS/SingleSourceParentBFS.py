import time
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType
from pyspark.sql import functions as F  # <-- Добавить эту строку


class SSBFS:
    def __enter__(self):
        self.spark = SparkSession.builder \
            .appName("SSBFS") \
            .master("local[*]") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .getOrCreate()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.spark.stop()

    def load_data_from_dataset(self, dataset):
        # Чтение и фильтрация данных
        edges_rdd = self.spark.read.text(dataset).rdd \
            .map(lambda line: tuple(map(int, line[0].split()))) \
            .filter(lambda x: len(x) == 2)

        # Создание DataFrame и добавление обратных рёбер
        edges_df = self.spark.createDataFrame(edges_rdd, ["src", "dst"])
        reversed_df = edges_df.selectExpr("dst as src", "src as dst")
        edges_df = edges_df.union(reversed_df).distinct()
        return edges_df

    def run(self, data, start_vertex):
        # Создаем начальный фронт
        initial_df = self.spark.createDataFrame(
            [(start_vertex, None)],
            ["vertex", "parent"]
        )

        visited_df = initial_df.alias("visited")
        visited_df.cache()

        current_front = initial_df.alias("front")
        iteration = 0

        while True:
            print(f"\n--- Iteration {iteration} ---")
            iteration += 1

            # Шаг 1: Получаем соседей
            neighbors = current_front.join(
                data.alias("edges"),
                F.col("front.vertex") == F.col("edges.src"),
                "inner"
            ).select(
                F.col("edges.dst").alias("vertex"),
                F.col("front.vertex").alias("parent")
            ).distinct()

            # Шаг 2: Исключаем уже посещенные
            new_nodes = neighbors.join(
                visited_df.alias("visited"),
                F.col("vertex") == F.col("visited.vertex"),
                "left_anti"
            ).alias("new_nodes")

            # Проверяем условие остановки
            if new_nodes.rdd.isEmpty():
                break

            # Шаг 3: Обновляем данные
            visited_df = visited_df.select("vertex", "parent").union(
                new_nodes.select("vertex", "parent")
            ).alias("visited").cache()

            current_front = new_nodes.select(
                F.col("vertex").alias("vertex"),
                F.col("parent").alias("parent")
            ).alias("front").cache()

            # Форсируем вычисления
            visited_df.count()
            current_front.count()

            # Отладочный вывод
            print(f"New nodes found: {current_front.count()}")
            current_front.show(5, truncate=False)

        # Финальный результат
        print("\nBFS completed. Results:")
        visited_df.orderBy("vertex").show(20, truncate=False)
        print(f"Total nodes visited: {visited_df.count()}")


def main():
    path = "datasets/connected_graph_10k_maxdepth3.txt"  # Проверьте путь
    with SSBFS() as algo:
        data = algo.load_data_from_dataset(path)
        print("Total edges:", data.count())
        data.show(5, truncate=False)
        algo.run(data, start_vertex=1)


if __name__ == "__main__":
    main()
