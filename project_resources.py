from constants import *
import json, os, sys, re
#import xlwt, xlrd

path = os.path.realpath(__file__).replace("project_resources.py", "")
with open(path+"project.cfg", "r", encoding="utf-8") as f:
    cfg = [x.replace("\n", "") for x in f]

config = __import__(cfg[0])
config_data = config.config_data
config_data.update( { ROOT_PATH : cfg[1] } )
config_data.update( { PROJECT_PATH : config_data[ROOT_PATH]+config_data[PROJECT_NAME]+"/" } )
from syntax_resources import *


def build_correction_data(config_data):
    res_data = {}

    workbook = xlrd.open_workbook(config_data[PROJECT_NAME]+"/"+config_data[CORRECTION_FILENAME])
    for sheet in workbook.sheets():
        for i in range(1, sheet.nrows):
            if sheet.cell(i, OPERATION) != "":
                res_data.update( { int(sheet.cell(i, ID_TAG).value) : { "operation" : sheet.cell(i, OPERATION).value, "new_role" : sheet.cell(i, NEW_ROLE).value, "new_context_word" : sheet.cell(i, NEW_CONTEXT_WORD).value } } )

    return res_data


def open_correction_data(config_data, rewrite=False):
    correction_data = {}
    try:
        with open(config_data[PROJECT_NAME]+"/correction_data.json", "r", encoding="utf-8") as f:
            correction_data = json.load(f)

    except:
        IOError
        correction_data = build_correction_data(config_data)
        with open(config_data[PROJECT_NAME]+"/correction_data.json", "w", encoding="utf-8") as f:
            json.dump(correction_data, f)

    if rewrite:
        correction_data = build_correction_data(config_data)
        with open(config_data[PROJECT_NAME]+"/correction_data.json", "w", encoding="utf-8") as f:
            json.dump(correction_data, f)

    return correction_data




def filter_carbage(data, carbage_list):
    removed = []
    for i in range(0, len(data)):
        if len(data[i]["words"]) == 0: removed.append(i)
        for w in data[i]["words"]:
            if w[WORD] in carbage_list:
                removed.append(i)

    for r in reversed(removed):
        data.remove(data[r])
    return data

def open_data(config_data):
    filename = config_data[DATA_FILENAME]
    with open(filename, "r", encoding="utf-8") as f:
        data =  json.load(f)
        return filter_carbage(data["data"], config_data[GARBAGE_LIST])

def test_dir(dirname):
    try:os.listdir(dirname)
    except:
        IOError
        os.makedirs(dirname)

