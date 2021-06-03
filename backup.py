import os
import json
import io
import shutil
from distutils.dir_util import copy_tree

def writing():
    json_data = []
    with open('config.json', 'w') as outfile:
        json.dump(json_data, outfile, indent=4,ensure_ascii=False)

def recompile(compress=True):

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

if __name__ == "__main__":
    recompile()