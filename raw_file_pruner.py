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
    
    def __init__(self, base_name: str, full_name: str, file_size: int):
        self.base_name = base_name
        self.full_name = full_name
        self.file_size = file_size

    def __eq__(self, other):
        if isinstance(other, FileHandle):
            return self.base_name == other.base_name
        return False
    
    def __hash__(self):
        return hash(self.base_name)

def parse_args() -> argparse.Namespace:
    '''Get the args from the command line'''
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", '-t', action='store', type=str, default = '.', help="Delete aux files")
    parser.add_argument("--recursive", '-r', action="store_true", help="Recursive search and delete")
    parser.add_argument("--delete", '-d', action="store_true", help="Enable deletion")

    args = parser.parse_args()
    return args


def find_all_files_with_endings(target_directory: str, endings: List[str]) -> None:
    '''Find all heic files in the current directory, regardless of capitalization'''
    all_files = os.listdir(target_directory)
    files_with_endings = [x for x in all_files if any(x.lower().endswith(ending) for ending in endings)]
    
    file_handles = [FileHandle(x[:x.rindex(".")], x, os.path.getsize(target_directory + '/' + x)) for x in files_with_endings]
    
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


def find_and_prune(target: dir, recursive: bool = False, delete: bool = False) -> int:
    '''Find all heic files in the target directory, and convert them'''
    
    num_deleted = 0
    total_files_size = 0

    if recursive:
        target_directories = find_all_directories_without_hidden(target)
    else:
        target_directories = [target]
        
    for dir in target_directories:
        print("Searching for files in:", dir)

        all_jpgs_in_dir = find_all_files_with_endings(dir, JPG_ENDINGS)
        print("Found", len(all_jpgs_in_dir), "jpgs")
        
        all_raws_in_dir = find_all_files_with_endings(dir, RAW_ENDINGS)
        print("Found", len(all_raws_in_dir), "raws")

        files_to_delete = [raw for raw in all_raws_in_dir if raw not in all_jpgs_in_dir]
        print("Found", len(files_to_delete), "files to delete")

        if delete:
            for raw in files_to_delete:
                delete_file(raw.full_name)
                num_deleted += 1
                total_files_size += raw.file_size

        else:
            for raw in files_to_delete:
                print(f"Found: {raw.full_name} to delete")
                total_files_size += raw.file_size

    print(f"Deleted from: {target_directories}.")
    
    return num_deleted, total_files_size

if __name__ == "__main__":
    start_time = time.time()
    args = parse_args()

    start_time = time.time()
    num_deleted, total_files_size = find_and_prune(args.target, args.recursive, args.delete)
    total_files_size_gb = total_files_size / 2**30 
    end_time = time.time()

    print(f"Pruned {num_deleted} files: {total_files_size_gb} GB in {end_time - start_time} seconds")