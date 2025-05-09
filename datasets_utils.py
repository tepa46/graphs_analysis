from os import listdir, path

PATH_TO_DATASETS = "../../datasets"


def get_datasets_path():
    return [path.join(PATH_TO_DATASETS, i) for i in listdir(PATH_TO_DATASETS)]
