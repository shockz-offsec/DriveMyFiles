import os
import shutil
import datetime
from distutils.dir_util import copy_tree
import zipfile
from logger_settings import logger
import drive
from json_handler import json_handler


"""Compress all the files recursively into a zipfile located in the temp dir
Args: 
    dir_name: name of the temp files directory
    dir_path: pathe of the temp files direcory
"""
def compress(dir_name, dir_path):
    
    zp_name = dir_name + '.zip'
    zp_path = 'Temp\\' + zp_name
    
    zp_file =  zipfile.ZipFile(zp_path, 'w')
    
    logger.info("Compressing files ...")
    for root, subfolders, files in os.walk(dir_path):
        for filename in files:
                zp_file.write(os.path.join(root, filename), os.path.relpath(os.path.join(root,filename), 'Temp\\' + dir_name), compress_type = zipfile.ZIP_DEFLATED)
    
    zp_file.close()
    logger.info("All files compressed into "+ zp_path)
    drive.upload_drive(zp_path)


"""Unzip the zip file downloaded from google drive
Args: 
    zp_file: zipfile's path to unzip
    dest_dir: destination path
"""
def unzip(zp_path, dest_dir):
    logger.info("Unzipping...")
    zp_file = None
    try:
        zp_file = zipfile.ZipFile(zp_path)
    except:
        logger.error("File could not be opened")
    zp_file.extractall(dest_dir)
    zp_file.close()
    logger.info("Unzip completed")


"""Clean the temp directory
Args:
    temp_dir: temp's path
    
*Call it after upload the files to Google Drive
"""
def clean(temp_dir):
    logger.info("Cleaning temp files...")
    try:
        shutil.rmtree(temp_dir, ignore_errors=False, onerror=None)
        os.makedirs(temp_dir)
    except OSError as e:
        logger.error("Could not delete the directory - " + e.strerror)
    logger.info("Complete cleaning")


"""Extracts all the information from the directories specified in the configuration file, copying them to the temporary directory
Args:
    make_compression: True indicates that we want to compress, False indicates that we don't want to compress
"""
def recompile(update_pr):

    json_data = json_handler()
    
    if not json_data.get_list("DRIVE", "AUTHENTICATED"):
        logger.warning("No authenticated")
        return False
    
    lista = json_data.get_list("DIRECTORIES")

    # Name of the folder where the files are stored if not compressed
    now = datetime.datetime.now()
    dir_name = 'backupdrive' + now.strftime("_%d_%b_%Y_%H_%M_%S")
    dir_path = 'Temp/' + dir_name
    
    update_pr(percent=15)
    
    if not os.path.exists('Temp'):
        os.makedirs('Temp')
        # A container folder is created for each copy.
        os.makedirs(dir_path)
    update_pr(percent=37)
    logger.info("Copying files...")
    for ruta in lista:
        end_route = dir_path + '\\' + ruta.split('\\')[-1]
        if os.path.exists(ruta):
            if os.path.isdir(ruta):
                    copy_tree(str(ruta), end_route)
            else:
                shutil.copy2(str(ruta), end_route)
    logger.info("Copy completed")
    
    update_pr(percent=50)
    update_pr(percent=75)
    
    if(json_data.get_list("DRIVE", "COMPRESS")):
        compress(dir_name, dir_path)
    else:
        drive.upload_drive(dir_path)
        
    update_pr(percent=100)
    
    return True