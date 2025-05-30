import numpy as np
from graphblas import Matrix, semiring, binary

from src.algo.algo import Algo


class GBMSBFS(Algo):
    def _mspbfs(self, graph_matrix, sources):
        n = graph_matrix.nrows

        sources_number = len(sources)

        front = Matrix(bool, sources_number, n)
        visited = Matrix(bool, sources_number, n)
        parent = Matrix(int, sources_number, n)

        for i, source in enumerate(sources):
            front[i, source] = True
            visited[i, source] = True
            parent[i, source] = source

        while front.nvals > 0:
            next_parents = front.mxm(graph_matrix, semiring.any_secondi)

            not_visited = Matrix(bool, sources_number, n)
            not_visited[:, :] = 1
            not_visited = not_visited.ewise_add(visited, op=binary.minus)

            next_parents = next_parents.select(not_visited)

            if next_parents.nvals == 0:
                break

            visited(mask=next_parents.S) << True
            parent(mask=next_parents.S) << next_parents

            front = Matrix(bool, sources_number, n)
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
        self._mspbfs(matrix, additional_data)
