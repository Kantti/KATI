import sys

with open("project.cfg", "w", encoding="utf-8") as f:
    f.write(sys.argv[1]+"\n")
    f.write(sys.argv[0].replace("switch_project.py", ""))
