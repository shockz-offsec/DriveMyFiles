import json

class json_handler:

    """Write into the json file"""
    """
    @staticmethod
    def writing(json_data):
        json_data = json.load(open('config.json','r'))
        # Content..
        with open(self.filename, 'w') as outfile:
            json.dump(json_data, outfile, indent=4, ensure_ascii=False)
    """     
    @staticmethod  
    def get_list(section, subsection=None):
        json_data = json.load(open('config.json', 'r'))
        return list(json_data[section])