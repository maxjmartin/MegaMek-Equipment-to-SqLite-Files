from pathlib import Path
import sqlite3
import json
import xmltodict
from bs4 import BeautifulSoup

# First collect the path for all files to convert.
file_list = []
pathlist = Path('./vehicles').glob('**/*.blk')
for path in pathlist:
    path_in_str = str(path)   
    file_list.append(path_in_str);

# Setup the sqlite database
vehicle_db = sqlite3.connect("vehicle.db")

curs = vehicle_db.cursor()
try:
    curs.execute('''
CREATE TABLE "vehicles" (
	"variant"	TEXT NOT NULL DEFAULT '(base)',
	"chasis"	TEXT NOT NULL,
	"data"	    TEXT
);
''')
except Exception as e:
    print(e)


# Iterate throught the file list.
# Document any auto corrected files.
count = 0
corrected_list = []
for i in file_list:
    obj = {}
    try:
        # Loop through each file and get a text string of it's contents.
        # Then convert the contents to xml.
        vehicle_file = open(i, "r", encoding="utf-8")
        xml = vehicle_file.read()
        xml = BeautifulSoup(''.join(xml), 'html.parser')
        xml = '<root>\n' + xml.prettify() + '</root>'
        xml = xml.split('\n')
        
        # Do some syntax clean up, and add a root node.
        vehicle_atr = ''
        for val in xml:
            if not '#' in val:
                vehicle_atr += (val + '\n')
        vehicle_atr = vehicle_atr.replace(' equipment=""', '')
        vehicle_atr = vehicle_atr.replace(' id:=""', '')
        vehicle_atr = xmltodict.parse(vehicle_atr)
        vehicle_atr = vehicle_atr['root']

        # Convert multiline values in to lists.
        for key, val in vehicle_atr.items():
            if val and '\n' in val:
                val = val.split('\n')
            obj[key] = val
    except Exception as e:
        print(e)
    
    try:
        # Write the data to the database.
        if obj['model'] == None:
            obj['model'] = '(base)'
            corrected_list.append(obj['name'])
        curs.execute("INSERT INTO vehicles VALUES(?, ?, ?)", (obj['model'], obj['name'], json.dumps(obj)))
    except Exception as e:
        print(e)
        print(str(obj))
        break  
    count += 1

    vehicle_file.close()
    vehicle_db.commit()

print('count = ', count)
print('auto corrected = ', corrected_list)
