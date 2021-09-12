# efipy
**\- efipy stands for '*easy file iterator python*'**    
python based easy file iterator, with recursive option, and file filtering. useful when you need to apply some function to a set of files.
also could be described as a glob wrapper with UI, for example cna inquires path with file completion capabuilities, show progress bar, and has increased flexabuility.

## intent:    
I find this module is useful for automating day to day file iteration tasks, mostly on Windows where bash language is orders of magnitude weaker than python. so instead of writing some half cooked file iterator every time I need to get something done, I thought I would make this.
also, after making several projects that needed a file iterator with a nice UI, and after deciding that copying and pasting this code is tedious and unhealthy, I decided to make this thing a project and upload it ot pypi.

## Installation
```
pip install efipy
```

## requirments  
(pypi should download all of these automatically upon install)
- [prompt-toolkit](https://pypi.org/project/safer-prompt-toolkit/)
- [safer-prompt-toolkit](https://pypi.org/project/safer-prompt-toolkit/) - (optional)
- [tqdm](https://pypi.org/project/tqdm/) - (optional)

## documentation
#### run(func, root_path=None, b_recursive=False, files_filter="*", b_yield_folders=False)
run func on all files that match.  
Parameters:  
>  - func - a callable, the function to be executed for each matching file in directories.  
>    func receives a single parameter of type pathlib.Path and returns nothing.  
>  - root_path - defaults to None. a directory, or a file in which to iterate. if file is given than runs only on that one file. if None is given, will prompt the user for a path, with path auto-completion and validation.  
>  - b_recursive - defaults to False. if True, will search recursively in sub-folders. if False will limit search to current dir.   
>  - files_filter - defaults to "*" (allows any path). a filter to limit search results for files, see "glob" for further details. 
>  - b_yield_folders - defaults to False. weather to pass paths to folders (not files) to func as well (if you want to iterate on folders as well as files)
>  - b_progress_bar - if true uses tqdm to display progress of file iteration.

returns:
> - a list of pathlib.Path instances that contains all the paths that matched the search (the exact same ones that were sent to func).     
 
info: 
1. if you don't like the fact that func receives a complicated pathlib.Path instance, you can just write `path=str(path)` in context:
2. take advantage of the root_path=None option. when no root path is supplied, the computer will prompt you for a path with some nice UI.
```python
def func(path):
    path=str(path)
    # ... other code to do with path ...

efipy.run(func)

```

#### inquire_output_path(default)
prompts the user for an output path, and returns it. if path already exists, asks the user to confirm overwrite. also has path auto-completion and validation.  
Parameters:  
>  - default - the default path to prompt user with

returns:
> - the validated path the user entered     
 
## example usages
example 1:  
lets say I have a folder in which all the files are numbered. let's say I want to rename every third file, so that it ends wit a q, for example:  
```
 before:                    -> after:  
 file_one_000.txt   
 some_other_file_001.md  
 some_third_file_002.txt    -> some_third_file_002q.txt  
 some_fourth_file_003.txt  
 yea_dogs_004.txt  
 wow_005.log                -> wow_005q.log
``` 
```python
import os,efipy
def rename(path):
    # rename files that end with divide by 3
    if int(path.stem[-3:])%3 == 0:
        name_no_extention,extention = os.path.splitext(path)
        os.rename(path,name_no_extention + "q" + extention)

efipy.run(rename)
```

example 2:
```python
import efipy
def func(path):
    print(str(path))

efipy.run(func,root_path="some_root_folder",b_recursive=True,files_filter="*.q")
# when run on the following file tree, will produce the following output:

# file tree:
# ─── some_root_folder
#     ├── f0.q
#     ├── dir1
#     │   ├── f1.r
#     │   └── f2.q
#     └── dir2
#        ├── f3.q
#        └── f4.q

# output, the program will print out (maybe not in this order):
#  some_root_folder/f0.q
#  some_root_folder/dir1/f2.q
#  some_root_folder/dir2/f3.q
#  some_root_folder/dir2/f4.q
```

## tip for easy usage
if you open ipython, you can easily get the docstring for any function by writing '?' after it, for example writing `efipy.run?` will supply the docstring of efipy.run  
