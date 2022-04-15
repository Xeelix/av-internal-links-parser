import multiprocessing
import os
import shutil

# import colorama


def optimized_path(save_path):
    return os.path.join(os.curdir, save_path)


def check_directory_existing_and_create(directory):
    directory = optimized_path(directory)
    if os.path.exists(directory):
        shutil.rmtree(directory)  # Clear folder
    os.makedirs(directory)


threads_count = round(multiprocessing.cpu_count() * 1.7)
filename_parsed_links = "all_links.txt"
files_folder = "parsed_links"

keyword_to_parse = ""
find_hrefs_path = "found_hrefs.txt"

# colorama.init()
