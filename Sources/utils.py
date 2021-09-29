import os
import time
from logger_settings import logger
from Sources.json_handler import json_handler
from Sources.drive import get_size as cloud_size, get_files, del_backup
import shutil

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

"""Remove the oldest n local backups set by the user
"""
def local_cleaner():
    import stat
    
    json_data = json_handler()
    if json_data.get_list("OPTIONS", "DELETE_BACKUP_LOCAL"):
        dirs = os.listdir('Temp')
        dates = [time.ctime(os.path.getctime('Temp\\'+file)) for file in dirs]
        count = len(dates) - json_data.get_list("OPTIONS", "NUM_BACKUP_LOCAL")
        if count > 0:
            for file in dirs[0:count]:
                path = 'Temp\\' + file
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path, ignore_errors=True, onerror=lambda func, path, _: (os.chmod(path, stat.S_IWRITE), func(path)))
                    else:
                        os.remove(path)
                except OSError as e:
                        logger.error("Could not delete the directory - " + e.strerror)
            logger.info("Complete cleaning of local backups")

"""Remove the oldest n cloud backups set by the user
"""        
def cloud_cleaner():
    json_data = json_handler()
    if json_data.get_list("OPTIONS", "DELETE_BACKUP_CLOUD"):
        list_backups = get_files(True)
        if list_backups:
            count = len(list_backups) - json_data.get_list("OPTIONS", "NUM_BACKUP_CLOUD")
            if count > 0:
                for bkup in list(list_backups.keys())[0:count]:
                    del_backup(list_backups[bkup])
                logger.info("Complete cleaning of cloud backups")