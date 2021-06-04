import os
import json
import shutil
from distutils.dir_util import copy_tree
import zipfile
from logger_settings import logger

"""Write into the json file"""
def writing():
    json_data = json.load(open('config.json','r'))
    # Content..
    with open('config.json', 'w') as outfile:
        json.dump(json_data, outfile, indent=4,ensure_ascii=False)

"""Compress all the files recursively into a zipfile located in the temp dir"""
def compress():

    zp_name = 'backupdrive.zip'
    zp_path = 'temp\\' + zp_name
    zp_file =  zipfile.ZipFile(zp_path, 'w')
    
    logger.info("Compressing files ...")
    for root, subfolders, files in os.walk('temp'):
        for filename in files:
            if filename != zp_name:
                zp_file.write(os.path.join(root, filename), os.path.relpath(os.path.join(root,filename), 'temp'), compress_type = zipfile.ZIP_DEFLATED)
    
    zp_file.close()
    logger.info("All files compressed")

"""Unzip the zip file downloaded from google drive
Args: 
    zp_file: zipfile's path to unzip
    dest_dir: destination path
"""
def unzip(zp_path,dest_dir):
    logger.info("Unzipping...")
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
    
Call it after upload the files to Google Drive
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
def recompile(make_compression=True):

    json_data = json.load(open('config.json','r'))
    lista = list(json_data["DIRECTORIES"])
    
    if not os.path.exists('temp'):
        os.makedirs('temp')
    logger.info("Copying files...")
    for ruta in lista:
        if os.path.exists(ruta):
                if os.path.isdir(ruta):
                    copy_tree(str(ruta), 'temp')
                else:
                    shutil.copy2(str(ruta), 'temp')
    if(make_compression):
        compress()
    
if __name__ == "__main__":
    # execute this at the start of the script
    if not os.path.exists('temp'):
        os.makedirs('temp')
    
    # Test
    recompile()
    