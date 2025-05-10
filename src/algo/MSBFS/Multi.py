from pygraphblas import Matrix, BOOL, INT64, semiring

def multi_source_parent_bfs(A: Matrix, sources: list[int]) -> Matrix:
    """
    Выполняет BFS от нескольких источников сразу, возвращает матрицу родителей (S x n).
    Каждый ряд i в parent соответствует обходу из источника sources[i].
    """
    # Приводим матрицу смежности к целочисленному типу (для семиринга ANY_SECONDI требуется INT)
    A = A.astype(INT64)

    n = A.ncols             # число вершин графа
    S = len(sources)        # число источников
    # Матрица родителей (S x n), по умолчанию все элементы 0 (не посещены)
    parent = Matrix.sparse(INT64, S, n)
    # Булева матрица посещённых (S x n), для маскирования
    visited = Matrix.sparse(BOOL, S, n)
    # Текущий фронт (S x n), помечает активные вершины (в int используем 1 как метку)
    frontier = Matrix.sparse(INT64, S, n)

    # Инициализация: в каждый ряд ставим источник сам себе родителем, отмечаем посещённым и фронтом
    for i, src in enumerate(sources):
        parent[i, src] = src       # корень дерева указывает на себя
        visited[i, src] = True     # отметим источник как посещённый
        frontier[i, src] = 1       # добавим источник во фронт

    # Основной цикл BFS: пока есть вершины во фронте
    while frontier.nvals > 0:
        # Вычисляем новый фронт: смежные узлы от текущего фронта
        new_frontier = frontier.mxm(A, semiring=semiring.ANY_SECONDI)
        # Маскируем уже посещённые вершины (оставляем только новые)
        new_frontier(mask=visited, mask_comp=True)  # применяем отрицание маски

        # Если новых вершин нет – выход
        if new_frontier.nvals == 0:
            break

        # Обновляем parent и visited для новых вершин:
        # Используем структурную маску new_frontier.S (позиции, где появились новые значения).
        parent(new_frontier.S) << new_frontier
        visited(new_frontier.S) << True

        # Переходим к следующему фронту
        frontier = new_frontier

    return parent

# Пример использования (граф и список источников должны быть заранее подготовлены)
# A = ... # some Matrix of size n×n, adjacency
# sources = [s0, s1, s2, ...]
# parent_matrix = multi_source_parent_bfs(A, sources)