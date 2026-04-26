#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utility script to copy all PPT charts to a specified location
"""

import os
import shutil
import sys

def copy_charts_to_folder(destination):
    """Copy all charts to destination folder"""
    source_dir = 'ppt_charts'
    
    if not os.path.exists(source_dir):
        print("Error: ppt_charts directory not found!")
        return False
    
    if not os.path.exists(destination):
        os.makedirs(destination)
        print("Created destination folder: {}".format(destination))
    
    files_copied = 0
    for filename in sorted(os.listdir(source_dir)):
        if filename.endswith('.png'):
            src_path = os.path.join(source_dir, filename)
            dst_path = os.path.join(destination, filename)
            shutil.copy2(src_path, dst_path)
            files_copied += 1
            print("Copied: {}".format(filename))
    
    print("\nSuccess! {} charts copied to: {}".format(files_copied, destination))
    return True

if __name__ == '__main__':
    if len(sys.argv) > 1:
        destination = sys.argv[1]
    else:
        # Default to Desktop
        desktop = os.path.expanduser('~/Desktop')
        destination = os.path.join(desktop, 'PPT_Charts')
    
    copy_charts_to_folder(destination)
