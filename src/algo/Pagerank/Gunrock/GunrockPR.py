from src.algo.GunrockAlgo import GunrockAlgo
from pathlib import Path


class GunrockPR(GunrockAlgo):

    def __page_rank(self, alpha=0.85, eps=1e-6):
        self.run_process(
            Path("Pagerank", "Gunrock", "build", "bin", "pr"), [str(alpha), str(eps)]
        )

    def run(self, data, additional_data=None):
        self.__page_rank()
