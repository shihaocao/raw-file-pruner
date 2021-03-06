'''A python script for pruning RAW files that do not have a corresponding JPG in the same directory.'''


import argparse
from typing import List
import os
import time
import re


JPG_ENDINGS = [".jpg", ".jpeg"]
'''All endings that are considered JPG endings, or the endings that is used to determine what is kept.'''


RAW_ENDINGS = [".nef", ".raw"]
'''All the RAW file endings that are considered extraneous and should be pruned if no corresponding JPG is found.'''

class FileHandle:
    '''A class to handle a file along with relevant information such as base name, full name and file_size.'''

    def __init__(self, base_name: str, full_name: str, file_size: int):
        '''A constructor for the FileHandle class.
        
        args:
            base_name: The base name of the file.
            full_name: The full name of the file including ending and path
            file_size: The size of the file in bytes.
        '''
        self.base_name = base_name
        self.full_name = full_name
        self.file_size = file_size

    def __eq__(self, other):
        '''A method to compare two FileHandles, based on their base name has the same numbering.'''
        if isinstance(other, FileHandle):
            exact = self.base_name.lower() == other.base_name.lower()
            inside = self.base_name.lower() in other.base_name.lower()
            inside_other = other.base_name.lower() in self.base_name.lower()
            return exact or inside or inside_other
        return False
    
    def __hash__(self):
        '''A method to hash a FileHandle, based on its base name.'''
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
    '''Find all files with that ending in the current directory, regardless of capitalization
    
    args:
        target_directory: The directory to search in
        endings: the list of endings to consider searching for
        
    returns:
        all file handles that match the search and ending criteria
    '''
    all_files = os.listdir(target_directory)
    files_with_endings = [x for x in all_files if any(x.lower().endswith(ending) for ending in endings)]
    file_handles = [FileHandle(x[:x.rindex(".")], x, os.path.getsize(target_directory + '/' + x)) for x in files_with_endings]
    
    return file_handles


def find_all_directories_without_hidden(target: dir) -> List[str]:
    '''Find all directories in the target directory, and ignore hidden directories
    
    returns:
        all the directories in the target directory, excluding hidden directories
    '''
    all_directories = [x[0] for x in os.walk(target)]
    HIDDEN = r".*\.\w+"
    
    # find all directories that don't have pass through a hidden folder
    return [x for x in all_directories if not re.match(HIDDEN, x)]


def delete_file(file_name: str) -> None:
    '''Delete the at the given absolute path'''
    os.remove(file_name)
    print(f"Deleted file: {file_name}")


def find_and_prune(target: dir, recursive: bool = False, delete: bool = False) -> int:
    '''Find all RAW files in the target directory, and convert them'''
    
    num_deleted = 0
    total_files_size = 0

    if recursive:
        target_directories = find_all_directories_without_hidden(target)
    else:
        target_directories = [target]
        
    for dir in target_directories:
        print("Searching for files in:", dir)

        all_jpgs_in_dir = find_all_files_with_endings(dir, JPG_ENDINGS)
        
        all_raws_in_dir = find_all_files_with_endings(dir, RAW_ENDINGS)

        files_to_delete = [raw for raw in all_raws_in_dir if raw not in all_jpgs_in_dir]
        
        if files_to_delete:
            print("Found", len(all_jpgs_in_dir), "jpgs")
            print("Found", len(all_raws_in_dir), "raws")
            print("Found", len(files_to_delete), "files to delete")

        if delete:
            for raw in files_to_delete:
                delete_file(dir + "/" + raw.full_name)
                num_deleted += 1
                total_files_size += raw.file_size

        else:
            for raw in files_to_delete:
                print(f"Found: {raw.full_name} to delete")
                total_files_size += raw.file_size
    
    return num_deleted, total_files_size

if __name__ == "__main__":
    start_time = time.time()
    args = parse_args()

    start_time = time.time()
    num_deleted, total_files_size = find_and_prune(args.target, args.recursive, args.delete)
    total_files_size_gb = total_files_size / 2**30 
    end_time = time.time()

    print(f"Pruned {num_deleted} files: {total_files_size_gb} GB in {end_time - start_time} seconds")