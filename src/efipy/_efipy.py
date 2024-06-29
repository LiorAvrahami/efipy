from pathlib import Path
import os.path
import traceback
import threading
import functools

try:
    from safer_prompt_toolkit import prompt
except ImportError:
    from prompt_toolkit import prompt

from prompt_toolkit import validation, completion


def e():
    """
    print simple example to screen, to be copied and used
    """
    print("\n# example\n"
          "import os\n"
          "def f(p):\n"
          "\tpath = str(p)\n"
          "\tif path.split(\"_\")[0] == \"0\"\n"
          "\t\tos.rename(path,\"00\" + \"_\".join(path.split(\"_\")[1:]))\n"
          "efipy.run(f)\n")

    print("\n# template\n"
          "import os\n"
          "def f(p):\n"
          "\tpath = str(p)\n"
          "\t#your code here\n"
          "efipy.run(f)\n")


def run_slow(func, *args, **kwargs):
    """
    same signature as efipy.run
    """
    i = 0
    b_skip_wait_for_input = False

    def step(path):
        nonlocal i, b_skip_wait_for_input
        func(path)
        if not b_skip_wait_for_input:
            response = input(f"step {i} complete. press enter to continue, write \"run\" to continue without more stops.\n")
            if response == "run":
                b_skip_wait_for_input = True
        i += 1
    run(step, *args, **kwargs)


def run(func, root_path=None, files_filter="*", b_recursive=False, b_yield_folders=False, number_of_threads=1, b_skip_errors=True, errors_log_file=None, b_progress_bar=True):
    """
    :param func: func - a callable, the function to be executed for each matching file in directories.
                 func receives a single parameter of type pathlib.Path and returns nothing.
    :param root_path: root_path - defaults to None. a directory, or a file in which to iterate. if file is given than runs only on that one file. if None is given, will prompt the user for a path, with path auto completion and validation.
    :param files_filter: files_filter - defaults to "*" (allows any path). a filter to limit search results for files, see "glob" for further details.
    :param b_recursive: b_recursive - defaults to False. if True, will search recursively in sub-folders. if False will limit search to current dir.
    :param b_yield_folders: b_yield_folders - defaults to False. weather to pass paths to folders (not files) to func as well (if you want to iterate on folders as well as files)
    :param number_of_threads: the number of threads to be used in order to concurrently run on all files. select 1 in order to loop on files linearly.
    :param b_skip_errors: if True, then when error occurs while running func, prints it's traceback, and then proceeds to run func on the next path to be iterated.
    :param errors_log_file: if not None, prints error logs to the file at the path given. file is created & cleared when this function is called.
    :param b_progress_bar: if true uses tqdm to display progress of file iteration.
    :return: a list of pathlib.Path instances that contains all the paths that matched the search (the exact same ones that were sent to func).
    """

    if errors_log_file is not None:
        with open(errors_log_file, "w+") as f:
            pass

    # if root path not specified, prompt user for path
    if root_path is None:
        root_path = inquire_input_path()

    # find all paths to iterate on
    root_path = Path(root_path)
    if root_path.is_dir():
        paths = glob_wrapper(root_path, b_recursive, files_filter)
    else:
        # check if root_path meets the files_filter condition.
        if root_path in glob_wrapper(root_path.parent, False, files_filter):
            paths = [root_path]
        else:
            paths = []

    # handle progress bar
    if number_of_threads == 1:
        paths_iter = paths
        if b_progress_bar:
            try:
                from tqdm import tqdm
                paths_iter = tqdm(paths)
            except ImportError:
                print("can't import tqdm, progress won't be displayed")
        start_iterating(func, paths_iter, b_yield_folders, b_skip_errors, errors_log_file)
    if number_of_threads != 1:
        threads = []
        paths_iter = [paths[i::number_of_threads] for i in range(number_of_threads)]
        # do work via several threads
        for i in range(number_of_threads):
            new_thread = threading.Thread(target=start_iterating,
                                          kwargs={"func": func, "paths_iter": paths_iter[i],
                                                  "b_yield_folders": b_yield_folders,
                                                  "b_skip_errors": b_skip_errors, "errors_log_file": errors_log_file})
            new_thread.start()
            threads.append(new_thread)
        # wait for all threads to finish
        for thread in threads:
            thread.join()

    return paths


def glob_wrapper(root_path, b_recursive, files_filter):
    if type(files_filter) is str:
        if b_recursive:
            paths = list(root_path.rglob(files_filter))
        else:
            paths = list(root_path.glob(files_filter))
    elif type(files_filter) in [list, tuple]:
        paths = functools.reduce(lambda x, y: x + y, [list(glob_wrapper(root_path, b_recursive,
                                 single_file_filter)) for single_file_filter in files_filter])
    else:
        raise ValueError()
    return paths


def start_iterating(func, paths_iter, b_yield_folders, b_skip_errors, errors_log_file):
    # call func for each path
    for path in paths_iter:
        import time
        if b_yield_folders or not path.is_dir():
            if b_skip_errors:
                try:
                    func(path)
                except Exception as e:
                    error_message = f"Error occurred while processing path \"{path}\". here is the error message:\n\n" + \
                        traceback.format_exc()
                    if errors_log_file is not None:
                        with open(errors_log_file, "a+") as f:
                            f.write(error_message + "\n--------------------------------------------------------\n")
                    else:
                        print(error_message)
            else:
                func(path)


def inquire_input_path(promet_text="enter input path:\n", default="."):
    return prompt(
        promet_text,
        validator=validation.Validator.from_callable(path_validator, error_message="invalid path"),
        completer=completion.PathCompleter(),
        default=default
    )


def inquire_output_path(promet_text="enter output path:\n", default=""):
    while True:
        output_path = prompt(
            promet_text,
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
