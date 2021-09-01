import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
__package__ = "efipy.tests"

from ..src import efipy

expected_paths = [r"test_file_tree\t1\t4.q",r"test_file_tree\t3.q"]
paths = []
def func(path):
    paths.append(path)

efipy.run(func,root_path="test_file_tree",b_recursive=True,files_filter="*.q")

paths_rel = [os.path.relpath(p,os.path.dirname(__file__)) for p in paths]
paths_rel = sorted(list(map(os.path.normpath,paths_rel)))
expected_paths = sorted(list(map(os.path.normpath,expected_paths)))
assert paths_rel == expected_paths