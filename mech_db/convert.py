from pathlib import Path
import sqlite3
import json

# First collect the path for all files to convert.
file_list = []
pathlist = Path('.\mechs').glob('**/*.mtf')
for path in pathlist:
    path_in_str = str(path)   
    file_list.append(path_in_str);


# Setup the sqlite database
mech_db = sqlite3.connect("mech.db")

curs = mech_db.cursor()
try:
    curs.execute("CREATE TABLE mechs(variant, chasis, data)")
except Exception as e:
    print(e)

# Iterate throught the file list.
# Document any auto corrected files.
count = 0
corrected_list = []
for i in file_list:
    # Loop through each file and get a text string of it's contents.
    mech_file = open(i, "r", encoding="utf-8")
    mech = mech_file.read()
    
    mech = mech.split('\n')
    mech_atr = []

    for line in mech:
        mech_atr.append(line.split(':'))

    for i in range(len(mech_atr)):
        if mech_atr[i][-1] == '':
            mech_atr[i] = mech_atr[i][:-1]

    # Convert the text to a python dictionary.
    obj = {}
    for i in range(len(mech_atr)):
        #  First look for a single pair.
        if len(mech_atr[i]) == 2:
            obj[mech_atr[i][0]] = mech_atr[i][1]
        # create a string, list pair of three elements.
        if len(mech_atr[i]) == 3:
            obj[mech_atr[i][0]] = mech_atr[i][1:]
        # Create a string and list pair.
        # Iterate through all elements until an empty line is found.
        if len(mech_atr[i]) == 1:
            lst = []
            j = i
            while j < len(mech_atr) and len(mech_atr[j]):
                lst.append(mech_atr[j][0])
                j += 1
            obj[mech_atr[i][0]] = lst
            i = j

    # Write the dictionary to the database.
    # If there is a failure, we try again by 
    # manually setting the model attribute.
    # Some clan mechs are missing that for 
    # the base model of the mech.
    try:
        try:
            curs.execute("INSERT INTO mechs VALUES(?, ?, ?)", (obj['model'], obj['chassis'], json.dumps(obj)))
        except Exception as e:
            try:
                curs.execute("INSERT INTO mechs VALUES(?, ?, ?)", ('base', obj['chassis'], json.dumps(obj)))
                corrected_list.append(obj['chassis'])
            except Exception as e:
                # Collect the data to id the failed db wrtie.
                # Then break so the file can be reviewed.
                print(e)
                print(str(mech_file))
                print(str(obj))
                break  
        count += 1
    except:
        print(str(mech_file))
        break

    # Close the file and commit the db write.
    mech_file.close()
    mech_db.commit()

print('count = ', count)
print('auto corrected = ', corrected_list)
