from os import listdir, path

PATH_TO_DATASETS = "../../datasets"


def get_datasets_path():
    return [path.join(PATH_TO_DATASETS, i) for i in listdir(PATH_TO_DATASETS)]

def convert_txt_to_mtx_directed(input_path):
    with open(input_path, 'r') as f:
        edges = [tuple(map(int, line.strip().split())) for line in f if line.strip()]

    nodes = set()
    for u, v in edges:
        nodes.add(u)
        nodes.add(v)
    n_nodes = max(nodes) + 1

    return n_nodes, edges