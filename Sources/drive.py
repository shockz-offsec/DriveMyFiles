from subprocess import Popen
import subprocess
from logger_settings import logger
import os,shutil
from Sources.json_handler import json_handler
from Sources.backup import unzip


"""Uploads the files to google drive via gdrive
Args:
    path: path of the directory or zipfile 
    
*If make_compression is False a folder will be created to contain all the files.
"""
def upload_drive(path):
    logger.info("Uploading to google drive")
    args = []
    if os.path.exists(path):
        if os.path.isdir(path):
            args = ['gdrive\\gdrive.exe', 'upload', '-r', path]
        else:
            args = ['gdrive\\gdrive.exe', 'upload', path]
            
    p = None
    try:
        p = Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    except Exception as e:
        logger.error("Can't execute the upload process to Google Drive" + str(e))
        
    out, error = p.communicate()
    if out == 0:
        logger.error("An error occurred while uploading to google drive: " + error)
    elif error:
        logger.info("Your files have been uploaded successfully")


"""Saves the credentials provided by the user for the use of gdrive
*The file witch contains the credentials of gdrive will be placed in '../AppData/Roaming/.gdrive/'
"""
def get_credentials(token=None):
    base = os.getenv('APPDATA')+"\\.gdrive"
    old = base+"_old"
    if os.path.exists(base):
        os.rename(base, old)
    
    args = ['gdrive\\gdrive.exe', 'about']
    p = None
    try:
        p = Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    except Exception as e:
        logger.error("Can't execute the validation process of gdrive" + str(e))
    
    p.stdin.write(str(token))
    
    error = p.communicate()[1]
    
    if error:
        logger.error("Not valid token")
        if os.path.exists(old):
            os.rename(old, base)
        return False
    else:
        logger.info("Credentials saved")
        if os.path.exists(old): shutil.rmtree(old, ignore_errors=False, onerror=None)
        return True
     
"""Check if there's credentials in the computer, modifying the parameter in config's file according to the result
"""       
def auth_status():
    base = os.getenv('APPDATA')+"\\.gdrive"
    json_data = json_handler()

    if os.path.exists(base):
        json_data.write_field("DRIVE", True, "AUTHENTICATED")
    else:
        json_data.write_field("DRIVE", False, "AUTHENTICATED")
    

"""Download the files from google drive to local
Args:
    file_id: id of the file / directory that we want to download
    
* If it is a directory it will be downloaded, if it is a zip file the unzip method will be called.
"""
def download_drive(file_id, filename, update_pr=None):
    json_data = json_handler()
    
    if not json_data.get_list("DRIVE","AUTHENTICATED"):
        logger.warning("No authenticated")
        return False

    if not os.path.exists('Downloads'):
        os.makedirs('Downloads')
    
    file_path = "Downloads\\" + filename
    filename = filename.replace(".zip","")

    update_pr(percent=55) if (update_pr != None) else None
    args = 'gdrive\gdrive.exe download -r ' + str(file_id) + ' --path "Downloads"'
    print(args)
    out = ""
    try:
        out = subprocess.check_output(args, shell=False, stderr=subprocess.STDOUT)
    except Exception as e:
        logger.error("Can't download the backup: "+ str(e))
    
    if out: logger.info("Downloaded successfully")
    
    if file_path.endswith(".zip") and json_data.get_list("OPTIONS", "UNZIP"):
        update_pr(percent=74) if (update_pr != None) else None
        file_path_unzipped = "Downloads\\" + filename
        os.makedirs(file_path_unzipped)
        unzip(file_path, file_path_unzipped)
        os.remove(file_path)
    
    update_pr(percent=100) if (update_pr != None) else None
    


"""Get the used space, free space and total size of the google drive account.
Returns: used space, free space and total size of the google drive account respectively
"""
def get_size():
    
    json_data = json_handler()
    if not json_data.get_list("DRIVE","AUTHENTICATED"):
        logger.warning("No authenticated")
        return "0 GB", "0 GB", "0 GB", 0
    
    args = ['gdrive\\gdrive.exe', 'about']
    p = None
    try:
        p = Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    except Exception as e:
        logger.error("Cant execute the validation process of gdrive" + str(e))
    
    out, error = p.communicate()
    
    if error:
        logger.error("Can't retrive the size from Google Drive")
    else:
        logger.info("Size retrievered")
    
    # Get the relevant info from the output
    x = [item.split(': ') for item in out.split('\n')]  
    # Used space, free space, total space
    return x[1][1], x[2][1], x[3][1], get_percent(x[1][1].split(" "), x[3][1].split(" "))


"""This method takes care of deleting backups after a certain time or under a user-specified backup limit
Args:
    file_id: name of the file / directory that we want to delete
"""
def del_backup(file_id):
    json_data = json_handler()
    if not json_data.get_list("DRIVE","AUTHENTICATED"):
        logger.warning("No authenticated")
        return False
    
    args = ['gdrive\\gdrive.exe', 'delete', '-r', str(file_id)]
    p = None
    try:
        p = Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    except Exception as e:
        logger.error("Cant execute the validation process of gdrive" + str(e))
    
    out, error = p.communicate()
    if error:
        logger.error("Can't delete the backup")
    else:
        logger.info("Deleted: "+ str(file_id))


"""Auxiliar method which returns the percent of the cloud size left
Args:
    used: sized used
    total: total sized
"""
def get_percent(used, total):
    return round(float(used[0])/float(total[0])*100)

"""Gets the name and id of the backups uploaded to the cloud"""
def get_files(orderbydate):
    json_data = json_handler()
    if not json_data.get_list("DRIVE","AUTHENTICATED"):
        logger.warning("No authenticated")
        return False
    info = {}
    try:
        args = ""
        if orderbydate:
            args = 'gdrive\\gdrive.exe list --query \"name contains \'backupdrive\'\" --order \"createdTime asc\"'
        else:
            args = 'gdrive\\gdrive.exe list --query \"name contains \'backupdrive\'\" --order \"name desc\"'
        out = subprocess.check_output(args, shell=False, stderr=subprocess.STDOUT)
        out = str(out.decode("utf-8")).split("\n")[1:]
        lenght = len(out)
        
        for n in range(lenght-1):
            info[out[n].split()[1]] = out[n].split()[0]
    except Exception as e:
        logger.error("Can't retrive the backup's data " + str(e))
    
    if info: 
        logger.info("Backups data retrieved")
        return info
    else:
        return False
    