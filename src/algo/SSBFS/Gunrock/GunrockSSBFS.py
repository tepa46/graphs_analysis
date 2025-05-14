from pathlib import Path

from src.algo.GunrockAlgo import GunrockAlgo


class GunrockSSBFS(GunrockAlgo):
    def _sspbfs(self, source):
        self.run_process(Path("SSBFS", "Gunrock", "build", "bin", "ssbfs"), [str(source)])

    def run(self, data, additional_data=None):
        self._sspbfs(additional_data)
