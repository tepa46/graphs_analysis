from pathlib import Path

from src.algo.GunrockAlgo import GunrockAlgo


class GunrockMSBFS(GunrockAlgo):
    def _mspbfs(self, sources):
        self.run_process(Path("MSBFS", "Gunrock", "build", "bin", "msbfs"), [str(source) for source in sources])

    def run(self, data, additional_data=None):
        self._mspbfs(additional_data)
