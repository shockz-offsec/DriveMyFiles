import os
from logger_settings import logger
from json_handler import json_handler

"""Calculate the size of the files or the files of a directory
   Returns: size of the files/dirs, number of files and number of folders
"""
def get_size():
    
    json_data = json_handler()
    lista = json_data.get_list("DIRECTORIES")
    num_files = 0
    num_dir = 0
    total = 0
    logger.info("Starting to calculate size of the files ...")
    for ruta in lista:
        if os.path.exists(ruta):
            if os.path.isdir(ruta):
                num_dir += 1
                #print(get_size_format(get_directory_size(ruta)))
                total +=get_directory_size(ruta)
            else:
                num_files += 1
                #print(get_size_format(os.path.getsize(ruta)))
                total +=os.path.getsize(ruta)
    logger.info("Calculated size ...")
    return get_size_format(total), str(num_files), str(num_dir)

"""Calculate the size of the files  of a directory"""
def get_directory_size(directory):
    total = 0
    try:
        for entry in os.scandir(directory):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_directory_size(entry.path)
    except NotADirectoryError:
        logger.error("The file is not a directory")
        return os.path.getsize(directory)
    except PermissionError:
        logger.error("The user doesnt have permissions to access this file or directory")
        return 0
    return total

"""Translate bytes to a more expresive unit"""
def get_size_format(b,factor=1024):
    logger.info("Transforming to a more expressive unit ...")
    for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
        if b < factor:
            return f"{b:.2f} {unit}"
        b/= factor
    return f"{b:.2f}Y"


if __name__ == "__main__":
    print(get_size())