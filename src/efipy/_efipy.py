from pathlib import Path
import os.path
import sys
import traceback

try:
    from safer_prompt_toolkit import prompt
except ImportError:
    from prompt_toolkit import prompt

from prompt_toolkit import validation, completion


def run(func, root_path=None, files_filter="*", b_recursive=False, b_yield_folders=False, b_skip_errors=True, b_progress_bar = True):
    """
    :param func: func - a callable, the function to be executed for each matching file in directories.
                 func receives a single parameter of type pathlib.Path and returns nothing.
    :param root_path: root_path - defaults to None. a directory, or a file in which to iterate. if file is given than runs only on that one file. if None is given, will prompt the user for a path, with path auto completion and validation.
    :param files_filter: files_filter - defaults to "*" (allows any path). a filter to limit search results for files, see "glob" for further details.
    :param b_recursive: b_recursive - defaults to False. if True, will search recursively in sub-folders. if False will limit search to current dir.
    :param b_yield_folders: b_yield_folders - defaults to False. weather to pass paths to folders (not files) to func as well (if you want to iterate on folders as well as files)
    :param b_skip_errors: if True, then when error occurs while running func, prints it's traceback, and then proceeds to run func on the next path to be iterated.
    :param b_progress_bar: if true uses tqdm to display progress of file iteration.
    :return: a list of pathlib.Path instances that contains all the paths that matched the search (the exact same ones that were sent to func).
    """

    # if root path not specified, prompt user for path
    if root_path is None:
        root_path = inquire_input_path()

    # find all paths to iterate on
    root_path = Path(root_path)
    if root_path.is_dir():
        if b_recursive:
            paths = list(root_path.rglob(files_filter))
        else:
            paths = list(root_path.glob(files_filter))
    else:
        # check if root_path meets the files_filter condition.
        if root_path in list(root_path.parent.glob(files_filter)):
            paths = [root_path]
        else:
            paths = []

    # handle progress bar
    paths_iter = paths
    if b_progress_bar:
        try:
            from tqdm import tqdm
            paths_iter = tqdm(paths)
        except ImportError:
            print("can't import tqdm, progress won't be displayed")

    # call func for each path
    for path in paths_iter:
        if b_yield_folders or not path.is_dir():
            if b_skip_errors:
                try:
                    func(path)
                except Exception as e:
                    print(f"Error occurred while processing path \"{path}\". here is the error message:\n")
                    print(traceback.format_exc())
            else:
                func(path)

    return paths

def inquire_input_path(default = "."):
    return prompt(
            "enter input path:\n",
            validator=validation.Validator.from_callable(path_validator, error_message="invalid path"),
            completer=completion.PathCompleter(),
            default=default
        )

def inquire_output_path(default):
    while True:
        output_path = prompt(
            "enter output path:\n",
            default=default,
            completer=completion.PathCompleter()
        )

        # check if overwriting
        if os.path.isfile(output_path):
            if not prompt_yes_no("are you sure you want to overwrite this path?"):
                continue

        # check if path exists
        if not os.path.exists(os.path.dirname(output_path)):
            if not prompt_yes_no("path doesn't exist. do you accept the creation of this path?"):
                continue

        return output_path


def path_validator(text):
    return os.path.exists(text)


def prompt_yes_no(messege) -> bool:
    yes_no_list = ["yes", "no"]

    def validate_yes_no(text):
        return text in yes_no_list

    v = prompt(
        f"{messege}:(yes/no)\n",
        validator=validation.Validator.from_callable(validate_yes_no, error_message="enter yes or no."),
        # todo completer =
    )
    return v == yes_no_list[0]