import json
import os.path

csrf = raw_input("CSRF Token: ")
session = raw_input("Session: ")

# Write JSON, read YAML
json_blob = json.dumps({'csrf': csrf, 'session': session},
                       indent=3)
f = open(os.path.expanduser('~')+"/edxrest.yaml", "w")
f.write(json_blob)
f.close()

