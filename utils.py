import os
import json


"""Calculate the size of the files or the files of a directory"""
def get_size():
    json_data = json.load(open('config.json','r'))
    lista = list(json_data["DIRECTORIES"])
    total = 0
    for ruta in lista:
        if os.path.exists(ruta):
            if os.path.isdir(ruta):
                #print(get_size_format(get_directory_size(ruta)))
                total +=get_directory_size(ruta)
            else:
                #print(get_size_format(os.path.getsize(ruta)))
                total +=os.path.getsize(ruta)
    return get_size_format(total)

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
        return os.path.getsize(directory)
    except PermissionError:
        return 0
    return total

"""Translate bytes to a more expresive unit"""
def get_size_format(b,factor=1024):
    for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
        if b < factor:
            return f"{b:.2f}{unit}"
        b/= factor
    return f"{b:.2f}Y"


if __name__ == "__main__":
    print(get_size())