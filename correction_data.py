from constants import *
from project_resources import *
import json
from syntax_resources import *
import os



def build_data(project_name):
    res_data = {}
    dirname = config_data[PROJECT_PATH]+"correction_data/"
    for filename in os.listdir(dirname):
        print(filename)
        with open(dirname+filename, "r", encoding="utf-8") as f:
            for row in f:
                if len(re.split("\t", row)) == 0: break
                row = re.split("\t", row)
                if row[OPERATION] != "":
                    id_tag = int(row[ID_TAG])
                    res_data.update( { id_tag : {} })
                    if row[OPERATION] == "out":
                        res_data[id_tag].update( { "out" : True } )
                    else:
                        if row[NEW_ROLE] != "":
                            res_data[id_tag].update( { "new_role" : CAT_NAMES.index(row[NEW_ROLE]) } )
                        if row[NEW_CONTEXT_WORD] != "":
                            res_data[id_tag].update( { "new_context_word" : row[NEW_CONTEXT_WORD] })

        return res_data


correction_data = {}
try:
    with open(config_data[ROOT_PATH]+config_data[PROJECT_NAME]+"/correction_data.json", "r", encoding="utf-8") as f:
        correction_data = json.load(f)

except:
    IOError
    correction_data = build_data(config_data[PROJECT_NAME])
    with open(config_data[ROOT_PATH]+config_data[PROJECT_NAME]+"/correction_data.json", "w", encoding="utf-8") as f:
        json.dump(correction_data, f)



