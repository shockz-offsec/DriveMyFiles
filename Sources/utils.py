import os
from logger_settings import logger
from Sources.json_handler import json_handler
from Sources.drive import get_size as cloud_size
import signal
from subprocess import check_output

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
                total += get_directory_size(ruta)
            else:
                num_files += 1
                total += os.path.getsize(ruta)
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

"""Sets the values of the local sizes in the json configuration file"""
def set_local_sizes():
    json_data = json_handler()
    size, num_files, num_folders = get_size()
    json_data.write_field("SIZES", num_files, "LOCAL_FILES")
    json_data.write_field("SIZES", num_folders, "LOCAL_FOLDERS")
    json_data.write_field("SIZES", size, "LOCAL_SIZE")

"""Sets the values of the cloud sizes in the json configuration file"""
def set_cloud_sizes():
    json_data = json_handler()
    used, free, total, percent = cloud_size()
    json_data.write_field("SIZES", used, "CLOUD_USED")
    json_data.write_field("SIZES", free, "CLOUD_FREE")
    json_data.write_field("SIZES", total, "CLOUD_TOTAL")
    json_data.write_field("SIZES", percent, "CLOUD_PERCENT")

"""Check if there is enough space to add one more element."""
def check_space_availability():
    json_data = json_handler()
    local_size = get_size()[0].split(" ")
    cloud_free = json_data.get_list("SIZES", "CLOUD_FREE").split(" ")
    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]
    if ((units.index(local_size[1]) >= units.index(cloud_free[1])) and (float(local_size[0]) >= (float(cloud_free[0])-0.3))):# Error margin of 300 MB
        print(units.index(local_size[1]),units.index(cloud_free[1]),local_size[0],float(cloud_free[0])-0.3)
        return False
    else:
        return True
