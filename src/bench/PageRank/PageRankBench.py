from src.bench.Bench import Bench


class PageRankBench(Bench):
    def collect_additional_data_lst(self, _) -> list:
        return [("", None)]
