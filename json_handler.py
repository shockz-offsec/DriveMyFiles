import json
import os
class json_handler:
    
    def __init__(self,filename="config.json"):
        self.filename = filename

    def get_list(self,section, subsection=None):
        json_data = json.load(open(self.filename, 'r'))
        if subsection:
            return json_data[section][subsection]
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
    
    def remove_field_list(self,section,number,subsection=None):
        with open(self.filename) as outfile:
            data = json.load(outfile)
            if subsection:
                del data[section][subsection][number]
            else:
                del data[section][number]
                
        with open(self.filename, "w") as outfile:
            json.dump(data, outfile,indent=4, ensure_ascii=False) 
    
    def edit_field_list(self,section,number,content,subsection=None):
        with open(self.filename) as outfile:
            data = json.load(outfile)
            if subsection:
                data[section][subsection][number] = content
            else:
                data[section][number] = content
                
        with open(self.filename, "w") as outfile:
            json.dump(data, outfile,indent=4, ensure_ascii=False)     