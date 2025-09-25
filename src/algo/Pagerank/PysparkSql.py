from typing import Optional

from src.algo.algo import Algo

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark import StorageLevel

from graphframes import GraphFrame


class SparkSQLPagerank(Algo):
    def __enter__(self):
        self.tmp_path = "/tmp/graph_checkpoints"
        self.spark = (
            SparkSession.builder.appName("pageRankPureSQL")
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
            .config("spark.driver.memory", "4g")
            .config("spark.executor.memory", "2g")
            .config("spark.executor.cores", "4")
            .config("spark.executor.instances", "2")
            .config(
                "spark.jars.packages", "graphframes:graphframes:0.8.2-spark3.1-s_2.12"
            )
            .getOrCreate()
        )
        self.sc = self.spark.sparkContext
        try:
            self.sc.setCheckpointDir(self.tmp_path)
        except Exception:
            pass

        try:
            default_parallelism = max(4, self.sc.defaultParallelism)
        except Exception:
            default_parallelism = 4
        self.spark.conf.set("spark.sql.shuffle.partitions", str(default_parallelism))
        self.num_partitions = default_parallelism

        self.broadcast_threshold = 50000

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            for t in ("outDeg", "ranks", "contribs_sum"):
                try:
                    self.spark.catalog.uncacheTable(t)
                except Exception:
                    pass
            self.spark.stop()
        except Exception:
            pass

    def load_data_from_dataset(self, dataset: str) -> GraphFrame:
        print("Loading data from dataset", dataset)
        raw = self.spark.read.text(str(dataset))

        edges_df = (
            raw.filter(~F.col("value").startswith("#"))
            .filter(F.length(F.col("value")) > 0)
            .select(
                F.split(F.col("value"), "\\s+").getItem(0).alias("src"),
                F.split(F.col("value"), "\\s+").getItem(1).alias("dst"),
            )
            .filter(F.col("src").isNotNull() & F.col("dst").isNotNull())
            .distinct()
        )

        vertices_df = (
            edges_df.select(F.col("src").alias("id"))
            .union(edges_df.select(F.col("dst").alias("id")))
            .distinct()
        )

        edges_df = edges_df.repartition(self.num_partitions, F.col("src")).persist(
            StorageLevel.MEMORY_AND_DISK
        )
        vertices_df = vertices_df.repartition(self.num_partitions, F.col("id")).persist(
            StorageLevel.MEMORY_AND_DISK
        )

        edges_df.createOrReplaceTempView("edges")
        vertices_df.createOrReplaceTempView("vertices")

        return GraphFrame(vertices_df, edges_df)

    def run(
        self,
        graph: GraphFrame,
        additional_data: Optional[dict] = None,
        alpha: float = 0.85,
        eps: float = 1e-6,
        max_iter: int = 100,
    ) -> GraphFrame:
        if graph is None:
            raise ValueError("graph is None")

        spark = self.spark

        # single count to get N
        N_row = spark.sql("SELECT COUNT(*) AS cnt FROM vertices").collect()
        if not N_row:
            return graph
        N = int(N_row[0]["cnt"])
        if N == 0:
            return graph

        spark.sql(
            """
            SELECT src AS id, COUNT(*) AS outDegree
            FROM edges
            GROUP BY src
            """
        ).createOrReplaceTempView("outDeg")
        try:
            spark.catalog.cacheTable("outDeg")
        except Exception:
            pass
        spark.sql("SELECT COUNT(*) FROM outDeg").collect()

        spark.sql(
            f"SELECT id, {1.0 / N} AS pagerank FROM vertices"
        ).createOrReplaceTempView("ranks")
        try:
            spark.catalog.cacheTable("ranks")
        except Exception:
            pass

        use_broadcast = N <= self.broadcast_threshold
        if use_broadcast:
            print(
                f"Using BROADCAST hints in SQL since N={N} <= {self.broadcast_threshold}"
            )

        for it in range(max_iter):
            print(f"Iteration {it}")

            if use_broadcast:
                contribs_sql = """
                    SELECT /*+ BROADCAST(ranks, outDeg) */ e.dst AS id,
                           SUM(r.pagerank / o.outDegree) AS sum_contribs
                    FROM edges e
                    JOIN ranks r ON e.src = r.id
                    JOIN outDeg o ON e.src = o.id
                    GROUP BY e.dst
                """
            else:
                contribs_sql = """
                    SELECT e.dst AS id,
                           SUM(r.pagerank / o.outDegree) AS sum_contribs
                    FROM edges e
                    JOIN ranks r ON e.src = r.id
                    JOIN outDeg o ON e.src = o.id
                    GROUP BY e.dst
                """

            spark.sql(contribs_sql).createOrReplaceTempView("contribs_sum")
            try:
                spark.catalog.cacheTable("contribs_sum")
            except Exception:
                pass

            spark.sql(
                f"""
                SELECT v.id AS id,
                       COALESCE(c.sum_contribs, 0.0) * {alpha} + {(1.0 - alpha) / N} AS pagerank
                FROM vertices v
                LEFT JOIN contribs_sum c ON v.id = c.id
                """
            ).createOrReplaceTempView("ranks_new")
            try:
                spark.catalog.cacheTable("ranks_new")
            except Exception:
                pass

            max_diff_row = spark.sql(
                """
                SELECT MAX(ABS(r.pagerank - rn.pagerank)) AS maxdiff
                FROM ranks r
                JOIN ranks_new rn ON r.id = rn.id
                """
            ).collect()
            max_diff = 0.0
            if max_diff_row and len(max_diff_row) > 0:
                val = max_diff_row[0]["maxdiff"]
                if val is not None:
                    max_diff = float(val)

            try:
                spark.catalog.uncacheTable("ranks")
            except Exception:
                pass
            spark.sql("SELECT id, pagerank FROM ranks_new").createOrReplaceTempView(
                "ranks"
            )
            try:
                spark.catalog.cacheTable("ranks")
            except Exception:
                pass

            try:
                spark.catalog.uncacheTable("contribs_sum")
            except Exception:
                pass
            try:
                spark.catalog.uncacheTable("ranks_new")
            except Exception:
                pass

            print(f"Iteration {it} finished, max_diff={max_diff}")
            if max_diff < eps:
                print("Converged.")
                break

        final_vertices_df = spark.sql(
            "SELECT v.id, r.pagerank FROM vertices v LEFT JOIN ranks r ON v.id = r.id"
        )
        edges_df = graph.edges
        return GraphFrame(final_vertices_df, edges_df)
