# raw-file-pruner
Recursively delete RAW/NEF files in a directory if the JPG version is missing.

# Installation
None. Just clone this script and run the python3 script.

# Usage
From the cloned github directory, run:

```
python3 raw_file_pruner.py -t <absolute_path_to_photo_dir> -d -r

```

This will delete all RAW/NEF files if the corresponding JPG or JPEG file is not present per directory recursively.


```
python3 raw_file_pruner.py -t <absolute_path_to_photo_dir>
```
Remove the `-d` argument to preview what you are deleting before you delete them.
Remove the `-r` argument if you do not want recurisve searching while pruning photos.