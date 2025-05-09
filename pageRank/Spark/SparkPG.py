from pyspark.sql import SparkSession, functions as F
from graphframes import GraphFrame
from os import listdir, path
from pyspark.sql.functions import col, lit, coalesce, abs as sql_abs, max as sql_max, sum as sql_sum

PATH_TO_DATASETS = "../../datasets"


def GetDatasetsPath():
    return [path.join(PATH_TO_DATASETS, i) for i in listdir(PATH_TO_DATASETS)]


def pagerank(graph: GraphFrame, alpha, eps: float, maxIter: int):
    N = graph.vertices.count()
    if N == 0:
        return graph

    vertices = graph.vertices
    edges = graph.edges
    ranks = vertices.select(col("id")).withColumn("pagerank", lit(1.0 / N))
    outDeg = graph.outDegrees

    for i in range(maxIter):
        print("Iteration {}".format(i))
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


def main():
    datasets = GetDatasetsPath()
    p = datasets[1]
    spark = (
        SparkSession.builder.appName("pageRank")
        .config("spark.jars.packages", "graphframes:graphframes:0.8.2-spark3.1-s_2.12")
        .getOrCreate()
    )

    raw_edges = spark.read.text(p)

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
    graph = GraphFrame(vertices, edges)
    result_graph = pagerank(graph, 0.85, 10e-8, 5)
    result_graph.vertices.orderBy(F.desc("pagerank")).show(20)
    spark.stop()


if __name__ == "__main__":
    main()
