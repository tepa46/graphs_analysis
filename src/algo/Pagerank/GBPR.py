import numpy as np
from graphblas import Matrix, Vector, binary, monoid, semiring, unary

from src.algo.algo import Algo


class GBPR(Algo):
    def _page_rank(self, graph_matrix: Matrix, alpha=0.85, eps=1e-6, max_iter=100):
        n = graph_matrix.nrows

        outdeg = graph_matrix.reduce_rowwise(monoid.plus)

        d_temp = outdeg.apply(binary.truediv, right=alpha)

        dmin = Vector(float, n)
        dmin[:] = 1.0 / alpha

        d = d_temp.ewise_add(dmin, op=monoid.max)

        rank = Vector(float, n)
        rank[:] = 1.0 / n

        teleport = Vector(float, n)
        teleport[:] = (1.0 - alpha) / n

        for _ in range(max_iter):
            t = rank

            w = t.ewise_mult(d, op=binary.truediv)

            temp = graph_matrix.T.mxv(w, op=semiring.plus_second)
            rank = teleport.ewise_add(temp)

            diff = t.ewise_union(rank, op=binary.minus, left_default=0.0, right_default=0.0)
            abs_diff = unary.abs(diff)
            error = float(abs_diff.reduce(monoid.plus))
            if error <= eps:
                break

    def load_data_from_dataset(self, dataset):
        edges = np.loadtxt(dataset, dtype=int, delimiter='\t')

        row_indices = edges[:, 0].tolist()
        col_indices = edges[:, 1].tolist()

        num_nodes = max(max(row_indices), max(col_indices)) + 1

        adj = Matrix.from_coo(row_indices, col_indices, 1, nrows=num_nodes, ncols=num_nodes)
        return adj

    def run(self, matrix, additional_data=None):
        self._page_rank(matrix)
