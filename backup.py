import os
import json
import shutil
from distutils.dir_util import copy_tree
import zipfile

"""Write into the json file"""
def writing():
    json_data = json.load(open('config.json','r'))
    # Content..
    with open('config.json', 'w') as outfile:
        json.dump(json_data, outfile, indent=4,ensure_ascii=False)

"""Compress all the files recursively into a zipfile located in the temp dir"""
def compress():

    json_data = json.load(open('config.json','r'))
    zp_name = 'backupdrive.zip'
    zp_path = json_data["GENERAL"]["TEMP_DIR"] + '\\' + zp_name
    zp_file =  zipfile.ZipFile(zp_path, 'w')
 
    for root, subfolders, files in os.walk(json_data["GENERAL"]["TEMP_DIR"]):
        for filename in files:
            if filename != zp_name:
                zp_file.write(os.path.join(root, filename), os.path.relpath(os.path.join(root,filename), json_data["GENERAL"]["TEMP_DIR"]), compress_type = zipfile.ZIP_DEFLATED)
    
    zp_file.close()

"""Unzip the zip file downloaded from google drive
Args: 
    zp_file: zipfile's path to unzip
    dest_dir: destination path
"""
def unzip(zp_path,dest_dir):
    zp_file = zipfile.ZipFile(zp_path)
    zp_file.extractall(dest_dir)
    zp_file.close()


"""Clean the temp directory
Args:
    temp_dir: temp's path
"""
def clean(temp_dir):
    try:
        shutil.rmtree(temp_dir, ignore_errors=False, onerror=None)
        os.makedirs(temp_dir)
    except OSError as e:
        print("Error:" + e.strerror)
    

"""Extracts all the information from the directories specified in the configuration file, copying them to the temporary directory
Args:
    make_compression: True indicates that we want to compress, False indicates that we don't want to compress
"""
def recompile(make_compression=True):

    json_data = json.load(open('config.json','r'))
    lista = list(json_data["DIRECTORIES"])
    
    if not os.path.exists(json_data["GENERAL"]["TEMP_DIR"]):
        os.makedirs(json_data["GENERAL"]["TEMP_DIR"])

    for ruta in lista:
        if os.path.exists(ruta):
                if os.path.isdir(ruta):
                    copy_tree(str(ruta), json_data["GENERAL"]["TEMP_DIR"])
                else:
                    shutil.copy2(str(ruta), json_data["GENERAL"]["TEMP_DIR"])
    if(make_compression):
        compress()

    
if __name__ == "__main__":
    #recompile()
    clean("C:\\Users\\Shockz\\Desktop\\MyBackupDrive\\temp")