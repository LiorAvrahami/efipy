import sys
import os
import pathlib
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

__package__ = ".".join(pathlib.Path(__file__).parts[-3:-1])

from ..src import efipy

def test_1():
    expected_paths = [r"test_file_tree\t1\t4.q",r"test_file_tree\t3.q"]
    paths = []
    def func(path):
        paths.append(path)

    path_to_test_file_tree = os.path.join(os.path.relpath(os.path.dirname(__file__),os.getcwd()),"test_file_tree")
    efipy.run(func,root_path=path_to_test_file_tree,b_recursive=True,files_filter="*.q")

    paths_rel = [os.path.relpath(p,os.path.dirname(__file__)) for p in paths]
    paths_rel = sorted(list(map(os.path.normpath,paths_rel)))
    expected_paths = sorted(list(map(os.path.normpath,expected_paths)))
    if paths_rel == expected_paths:
        print("success")
    else:
        raise AssertionError(f"paths_rel = {paths_rel}\nexpected_paths = {expected_paths}")

def test_2():
    expected_paths = [r"test_file_tree\t1\t4.q",r"test_file_tree\t1\t5.k",r"test_file_tree\t1\t6.k", r"test_file_tree\t3.q",r"test_file_tree\t7.k"]
    paths = []

    def func(path):
        paths.append(path)
        import threading
        print(f"{str(path)}, {threading.currentThread().getName()}\n")

    path_to_test_file_tree = os.path.join(os.path.relpath(os.path.dirname(__file__), os.getcwd()), "test_file_tree")
    efipy.run(func, root_path=path_to_test_file_tree, b_recursive=True,number_of_threads=3, files_filter=["*.q","*.k"])

    paths_rel = [os.path.relpath(p, os.path.dirname(__file__)) for p in paths]
    paths_rel = sorted(list(map(os.path.normpath, paths_rel)))
    expected_paths = sorted(list(map(os.path.normpath, expected_paths)))
    if paths_rel == expected_paths:
        print("success")
    else:
        raise AssertionError(f"paths_rel = {paths_rel}\nexpected_paths = {expected_paths}")

if __name__ == "__main__":
    test_1()
    test_2()