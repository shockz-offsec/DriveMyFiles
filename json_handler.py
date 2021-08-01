import json
import os
class json_handler:
    
    def __init__(self,filename="config.json"):
        self.filename = filename

    """Write into the json file"""
    """
    @staticmethod
    def writing(json_data):
        json_data = json.load(open('config.json','r'))
        # Content..
        with open(self.filename, 'w') as outfile:
            json.dump(json_data, outfile, indent=4, ensure_ascii=False)
    """     
    def get_list(self,section, subsection=None):
        json_data = json.load(open(self.filename, 'r'))
        return list(json_data[section])
    
    def write_field(self,section,content,subsection=None):
        
        with open(self.filename) as outfile:
            json_data = json.load(outfile)   
                 
            if subsection:
                json_data[section][subsection] = content

            else:   
                json_data[section] = content

        with open(self.filename, 'w') as f:
            json.dump(json_data, f,indent=4, ensure_ascii=False)

    def add_field_list(self,section,content,subsection=None):

        with open(self.filename) as outfile:
            json_data = json.load(outfile)
        if subsection:
            temp = list(json_data[section][subsection])
            temp.append(content)
            json_data[section][subsection] = temp

        else:   
            temp = list(json_data[section])
            temp.append(content)
            json_data[section] = temp

        with open(self.filename, 'w') as f:
            json.dump(json_data, f,indent=4, ensure_ascii=False) 