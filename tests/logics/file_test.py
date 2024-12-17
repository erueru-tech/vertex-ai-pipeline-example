import os
import tempfile

from src.logics.file import make_parent_dirs_and_return_path


def test_make_parent_dirs_and_return_path1() -> None:
    parent_dir_path = f"{tempfile.gettempdir()}/tmp/tests/logics/file_test"
    if os.path.exists(parent_dir_path):
        os.rmdir(parent_dir_path)
    file_path = f"{parent_dir_path}/test_make_parent_dirs_and_return_path1.yaml"
    return_path = make_parent_dirs_and_return_path(file_path)
    assert os.path.exists(parent_dir_path)
    assert parent_dir_path == return_path
