import os

from algo import Algo
from utils import convert_txt_to_mtx_directed
import subprocess

class GunrockPR(Algo):

    __default_graph_path = "graph.mtx"

    def load_data_from_dataset(self, dataset):
        return convert_txt_to_mtx_directed(dataset)

    def run(self, data):
        n_nodes, edges = data
        with open(self.__default_graph_path, 'w') as f:
            f.write("%%MatrixMarket matrix coordinate pattern general\n")
            f.write(f"{n_nodes} {n_nodes} {len(edges)}\n")
            for u, v in edges:
                f.write(f"{u+1} {v+1}\n")

        subprocess.run(["gunrock/build/bin/pr", "-m", self.__default_graph_path])

        os.remove(self.__default_graph_path)