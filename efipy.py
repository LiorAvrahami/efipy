from pathlib import Path
import os.path
import sys
from safer_prompt_toolkit import prompt, validation, completion


def run(func, root_path=None, b_recursive=False, files_filter="*", b_yield_folders=False, b_inquire_output=False):
    if root_path is None:
        root_path = prompt(
            "enter path:\n",
            validator=validation.Validator.from_callable(path_validator, error_message="invalid path"),
            completer=completion.PathCompleter()
        )
    if b_inquire_output:
        inquire_output_path(default=os.path.join(root_path, "output"))

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
    for path in paths:
        if b_yield_folders or not path.is_dir():
            func(path)
    return paths


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
        if not os.path.exists(os.path.split(output_path)[0]):
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