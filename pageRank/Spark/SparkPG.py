from pyspark.sql import SparkSession, functions as F
from graphframes import GraphFrame
from pyspark.sql.functions import col, lit, coalesce, abs as sql_abs, max as sql_max, sum as sql_sum

from algo import Algo

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

    def _page_rank(self, graph: GraphFrame, alpha=0.85, eps=1e-8, max_iter=20):
        N = graph.vertices.count()
        if N == 0:
            return graph

        vertices = graph.vertices
        edges = graph.edges
        ranks = vertices.select(col("id")).withColumn("pagerank", lit(1.0 / N))
        outDeg = graph.outDegrees

        for i in range(max_iter):
            # print("Iteration {}".format(i))
            # Contributions of each vertex to its neighbors
            contribs = (edges.join(ranks, edges["src"] == ranks["id"])
                        .join(outDeg, edges["src"] == outDeg["id"])
                        .select(edges["dst"].alias("id"),
                                (ranks["pagerank"] / outDeg["outDegree"]).alias("contrib")))

            # Sum contributions per destination vertex
            contribs_sum = contribs.groupBy("id").agg(sql_sum("contrib").alias("sum_contribs"))

            # Compute new pagerank values: teleport + contributions
            ranks_new = (vertices.select(col("id"))
                         .join(contribs_sum, "id", how="left")
                         .select(col("id"),
                                 coalesce(col("sum_contribs"), lit(0.0)).alias("sum_contribs"))
                         .withColumn("pagerank", lit((1 - alpha) / N) + (lit(alpha) * col("sum_contribs"))))

            diff = (ranks.join(ranks_new, "id")
                    .withColumn("diff", sql_abs(ranks["pagerank"] - ranks_new["pagerank"])))
            max_diff = diff.agg(sql_max("diff")).collect()[0][0]

            # Update ranks for next iteration
            ranks = ranks_new.select("id", "pagerank")
            if max_diff < eps:
                break

        final_vertices = vertices.join(ranks, "id", how="left")
        return GraphFrame(final_vertices, edges)

    def load_data_from_dataset(self, dataset):
        raw_edges = self.spark.read.text(dataset)

        edges = (
            raw_edges
                .filter(~F.col("value").startswith("#"))
                .filter(F.length(F.col("value")) > 0)
                .select(
                F.split(F.col("value"), "\\s+")[0].alias("src"),
                F.split(F.col("value"), "\\s+")[1].alias("dst")
            )
        )

        vertices = (
            edges.select(F.col("src").alias("id"))
                .union(edges.select(F.col("dst").alias("id")))
                .distinct()
        )

        return GraphFrame(vertices, edges)

    def run(self, graph_frame):
        self._page_rank(graph_frame)
        # result_graph.vertices.orderBy(F.desc("pagerank")).show(20)
