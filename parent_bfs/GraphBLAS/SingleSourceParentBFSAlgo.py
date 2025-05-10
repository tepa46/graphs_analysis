import numpy as np
from graphblas import Matrix, Vector, semiring, binary

from algo import Algo


class SingleSourceParentBFSAlgo(Algo):
    def _sspbfs(self, graph_matrix, source):
        n = graph_matrix.nrows
        # print(n)
        # print(graph_matrix.to_dense(fill_value=-1))

        front = Vector(bool, n)
        front[source] = True
        # print("front", front.to_dense(fill_value=-1))
        visited = Vector(bool, n)
        visited[source] = True
        # print("visited", visited.to_dense(fill_value=-1))
        parent = Vector(int, n)  # parent indeces
        parent[source] = source
        # print("parent", parent.to_dense(fill_value=-1))

        while front.nvals > 0:
            next_parents = front.vxm(graph_matrix, semiring.any_secondi)
            # print("next_parents", next_parents.to_dense(fill_value=-1))

            not_visited = Vector(bool, n)
            not_visited[:] = 1
            not_visited = not_visited.ewise_add(visited, op=binary.minus)
            # print("not_visited", not_visited.to_dense(fill_value=-1))

            next_parents = next_parents.select(not_visited)
            # print("next_parents2", next_parents.to_dense(fill_value=-1))

            if next_parents.nvals == 0:
                break

            visited(mask=next_parents.S) << True
            parent(mask=next_parents.S) << next_parents

            front = Vector(bool, n)
            front(mask=next_parents.S) << True

        # print(parent.to_dense(fill_value=-1))

    def load_data_from_dataset(self, dataset):
        edges = np.loadtxt(dataset, dtype=int, delimiter='\t')

        d_row_indices = edges[:, 0].tolist()
        d_col_indices = edges[:, 1].tolist()

        row_indeces = d_row_indices + d_col_indices
        col_indices = d_col_indices + d_row_indices

        adj = Matrix.from_coo(row_indeces, col_indices, True)
        return adj

    def run(self, matrix, additional_data=None):
        self._sspbfs(matrix, additional_data)
