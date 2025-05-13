import os
import subprocess

from src.algo.algo import Algo
from src.dataset_utils import get_mtx_from_txt
from pathlib import Path

class GunrockPR(Algo):

    __default_graph_path = "graph.mtx"

    def load_data_from_dataset(self, dataset):
        return get_mtx_from_txt(dataset)

    def run(self, data, additional_data=None):
        project_root = Path(__file__).resolve().parents[3]
        pr_root = project_root / "gunrock" / "build" / "bin" / "pr"
        n_nodes, edges = data
        with open(self.__default_graph_path, 'w') as f:
            f.write("%%MatrixMarket matrix coordinate pattern general\n")
            f.write(f"{n_nodes} {n_nodes} {len(edges)}\n")
            for u, v in edges:
                f.write(f"{u+1} {v+1}\n")

        subprocess.run([pr_root, "-m", self.__default_graph_path])

        os.remove(self.__default_graph_path)