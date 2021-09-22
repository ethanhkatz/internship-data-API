import fileinput
import json

#empty existing log file
with open("log.txt", 'w') as log:
    log.write('')

with open("log.txt", 'a') as log:
    for line in fileinput.input():
        json_object = json.loads(line)
        log.write(json.dumps(json_object, indent=2))
        log.write("\n\n------------------------------------------------------------\n\n")
