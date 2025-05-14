import os
import subprocess

from src.algo.algo import Algo
from src.dataset_utils import get_mtx_from_txt
from pathlib import Path


class GunrockAlgo(Algo):
    __default_graph_name = "graph.mtx"
    __graph_path = Path(__file__).parent / __default_graph_name

    def run_process(self, cuda_algo_path, params_lst):
        project_root = Path(__file__).resolve().parent
        algo_exec = project_root / cuda_algo_path
        subprocess.run([algo_exec, self.__graph_path.resolve(), *params_lst])

    def load_data_from_dataset(self, dataset):
        n_nodes, edges = get_mtx_from_txt(dataset)
        with open(self.__graph_path, 'w') as f:
            f.write("%%MatrixMarket matrix coordinate pattern general\n")
            f.write(f"{n_nodes} {n_nodes} {len(edges)}\n")
            for u, v in edges:
                f.write(f"{u + 1} {v + 1}\n")
        return None

    def run(self, data, additional_data=None):
        pass
