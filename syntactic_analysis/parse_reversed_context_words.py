import json, os, sys, csv, re, xlwt
from Context import *
from syntax_resources import *
from project_resources import *

project_name = "test_sekunti"

try:
    config = __import__(project_name)
    config_data = config.config_data
except:
    ImportError
    sys.exit("No config file found")


data = open_data(config_data)

for row in data:
    context = Context(row, config_data, direction="reversed", role=NP_ATTRIBUTE)
    if len(context.res_words) > 0: print(context.res_words)


