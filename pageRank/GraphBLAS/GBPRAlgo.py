import numpy as np
from graphblas import Matrix, Vector, binary, monoid, semiring, unary

from algo import Algo


class GBPRAlgo(Algo):
    def _page_rank(self, graph_matrix: Matrix, alpha=0.85, eps=1e-8, max_iter=20):
        n = graph_matrix.nrows

        outdeg = graph_matrix.reduce_rowwise(monoid.plus)

        # outdeg / d
        # d_temp = gb.Vector(float, n)
        d_temp = outdeg.apply(binary.truediv, right=alpha)

        dmin = Vector(float, n)
        dmin[:] = 1.0 / alpha

        # d = gb.Vector(float, n)
        d = d_temp.ewise_add(dmin, op=monoid.max)

        rank = Vector(float, n)
        rank[:] = 1.0 / n

        teleport = Vector(float, n)
        teleport[:] = (1.0 - alpha) / n

        for _ in range(max_iter):
            t = rank

            # w = gb.Vector(float, n)
            w = t.ewise_mult(d, op=binary.truediv)

            temp = graph_matrix.T.mxv(w, op=semiring.plus_second)
            rank = teleport.ewise_add(temp)
            # rank = teleport + temp

            # diff = gb.Vector(float, n)
            diff = t.ewise_union(rank, op=binary.minus, left_default=0.0, right_default=0.0)
            abs_diff = unary.abs(diff)
            error = float(abs_diff.reduce(monoid.plus))
            if error <= eps:
                break

        # print(sorted(rank.to_dense(), reverse=True)[:5])
        # print(rank.to_dense().sum())

    def load_data_from_dataset(self, dataset):
        edges = np.loadtxt(dataset, dtype=int, delimiter='\t')

        row_indices = edges[:, 0].tolist()
        col_indices = edges[:, 1].tolist()

        adj = Matrix.from_coo(row_indices, col_indices, 1)
        return adj

    def run(self, matrix):
        self._page_rank(matrix)
