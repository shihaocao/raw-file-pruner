'''A python script for pruning raw files.'''


import argparse
from typing import List
import os
import time
import re


# CMD = "heif-convert"
# QUALITY = "-q"
# QUALITY_ARG = "99"
# AUX_FILE_SUFFIX = "-urn:com:apple:photo:2020:aux:hdrgainmap"
JPG_ENDINGS = [".jpg", ".jpeg"]
RAW_ENDINGS = [".nef", ".raw"]


class FileHandle:
    
    def __init__(self, base_name: str, full_name: str):
        self.base_name = base_name
        self.full_name = full_name
        
    def __eq__(self, other):
        if isinstance(other, FileHandle):
            return self.base_name == other.base_name
        return False
    
    def __hash__(self):
        return hash(self.base_name)

def parse_args() -> argparse.Namespace:
    '''Get the args from the command line'''
    parser = argparse.ArgumentParser()
    parser.add_argument("--search-dir", default = '.', help="Delete aux files")
    parser.add_argument("--recursive", action="store_true", help="Recursive search and delete")
    parser.add_argument("--view", action="store_true", help="View only")

    args = parser.parse_args()
    return args


def find_all_files_with_endings(target_directory: str, endings: List[str]) -> None:
    '''Find all heic files in the current directory, regardless of capitalization'''
    all_files = os.listdir(target_directory)
    files_with_endings = [x for x in all_files if any(x.lower().endswith(ending) for ending in endings)]
    
    file_handles = [FileHandle(x[:x.rindex(".")], x) for x in files_with_endings]
    
    return file_handles


def find_all_directories_without_hidden(target: dir) -> List[str]:
    all_directories = [x[0] for x in os.walk(target)]
            
    HIDDEN = r".*\.\w+"
    
    # find all directories that don't have pass through a hidden folder
    return [x for x in all_directories if not re.match(HIDDEN, x)]


def delete_file(file_name: str) -> None:
    '''Delete the file'''
    os.remove(file_name)
    print(f"Deleted file: {file_name}")


def find_and_prune(target: dir, recursive: bool = False, view: bool = False) -> None:
    '''Find all heic files in the target directory, and convert them'''
    
    if recursive:
        target_directories = find_all_directories_without_hidden(target)
    else:
        target_directories = [target]
        
    for dir in target_directories:
        print("Searching for files in:", dir)
    # find all directory paths
        # for a given directory
    
        # find all JPGS
        all_jpgs_in_dir = find_all_files_with_endings(dir, JPG_ENDINGS)
        print("Found", len(all_jpgs_in_dir), "jpgs")
        # find all RAWS
        all_raws_in_dir = find_all_files_with_endings(dir, RAW_ENDINGS)
        print("Found", len(all_raws_in_dir), "raws")

        # if RAW exists, but JPG does not, delete raw
        files_to_delete = [raw for raw in all_raws_in_dir if raw not in all_jpgs_in_dir]
        print("Found", len(files_to_delete), "files to delete")

        if view:
            for raw in files_to_delete:
                print(f"Found: {raw.full_name} to delete")
        else:
            for raw in files_to_delete:
                delete_file(raw.full_name)


if __name__ == "__main__":
    start_time = time.time()
    args = parse_args()
    # print(f'Found {len(heics)} heic files in this directory.')

    start_time = time.time()
    find_and_prune(args.search_dir, args.recursive, args.view)
    
    end_time = time.time()
    heics = []
    print(f'Converted {len(heics)} heic files in {end_time - start_time} seconds.')