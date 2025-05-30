import numpy as np
from graphblas import Matrix, Vector, semiring, binary

from src.algo.algo import Algo


class GBSSBFS(Algo):
    def _sspbfs(self, graph_matrix, source):
        n = graph_matrix.nrows

        front = Vector(bool, n)
        front[source] = True

        visited = Vector(bool, n)
        visited[source] = True

        parent = Vector(int, n)
        parent[source] = source

        while front.nvals > 0:
            next_parents = front.vxm(graph_matrix, semiring.any_secondi)

            not_visited = Vector(bool, n)
            not_visited[:] = 1
            not_visited = not_visited.ewise_add(visited, op=binary.minus)

            next_parents = next_parents.select(not_visited)

            if next_parents.nvals == 0:
                break

            visited(mask=next_parents.S) << True
            parent(mask=next_parents.S) << next_parents

            front = Vector(bool, n)
            front(mask=next_parents.S) << True

    def load_data_from_dataset(self, dataset):
        edges = np.loadtxt(dataset, dtype=int, delimiter="\t")

        row_indices = edges[:, 0].tolist()
        col_indices = edges[:, 1].tolist()

        num_nodes = max(max(row_indices), max(col_indices)) + 1

        adj = Matrix.from_coo(
            row_indices, col_indices, True, nrows=num_nodes, ncols=num_nodes
        )
        return adj

    def run(self, matrix, additional_data=None):
        self._sspbfs(matrix, additional_data)
