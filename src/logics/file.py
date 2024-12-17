import os


def make_parent_dirs_and_return_path(file_path: str) -> str:
    dir_path = os.path.dirname(file_path)
    os.makedirs(dir_path, exist_ok=True)
    return dir_path
