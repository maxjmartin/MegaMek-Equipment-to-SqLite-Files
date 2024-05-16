import math
from pathlib import Path
import sqlite3
import json

def initAttributes(mech):
    mech_atr = []
    for line in mech:  
        #  Make pairs.
        mech_atr.append(line.split(':'))
        mech_atr[-1][0] = mech_atr[-1][0].lower()
    return mech_atr

def simplifyLongPairs(mech_atr):
    for i in range(len(mech_atr)):
        #  Simplify long pairs.
        if len(mech_atr[i]) > 2:
            mech_atr[i] = [mech_atr[i][0], mech_atr[i][1:]]
    return mech_atr

def defineCriticalLocations(mech_atr):
    for i in range(len(mech_atr)):
        # Define the critical tables.
        if isCriticalTable(mech_atr[i]):
            start_loc = i
            i += 1
            crit_list = []
            while notEmptyLine(mech_atr[i]):
                crit_list.append(mech_atr[i][0])
                mech_atr[i] = ['']
                i += 1
            mech_atr[start_loc][-1] = crit_list
    return mech_atr

def defineWeaponsList(mech_atr):
    for i in range(len(mech_atr)):
        # Define the weapons list.
        text = mech_atr[i][0]
        if text.lower() == 'weapons':
            start_loc = i
            i += 1
            weapons_list = []
            while notEmptyLine(mech_atr[i]):
                weapons_list.append(mech_atr[i][0].split(', '))
                mech_atr[i] = ['']
                i += 1
            mech_atr[start_loc][-1] = weapons_list
    return mech_atr

def defineArmorList(mech_atr):
    for i in range(len(mech_atr)):
        # Define the armor list.
        text = mech_atr[i][0]
        if text.lower() == 'armor':
            start_loc = i
            i += 1
            armor_list = []
            while notEmptyLine(mech_atr[i]):
                armor_list.append(mech_atr[i])
                mech_atr[i] = ['']
                i += 1
            mech_atr[start_loc].append(makeDict(armor_list))
    return mech_atr

# Define an empty line test.
def notEmptyLine(line):
    for i in line:
        if i != '':
            return True
    return False

# Determine if a critical table needs to be defined.
def isCriticalTable(line):
    if len(line) == 2 and line[-1] == '':
        text = line[0].lower()
        if text == 'left arm':
            return True
        if text == 'right arm':
            return True
        if text == 'left leg':
            return True
        if text == 'right leg':
            return True
        if text == 'left torso':
            return True
        if text == 'right torso':
            return True
        if text == 'center torso':
            return True
        if text == 'head':
            return True
    return False

# Determine if a critical table needs to be defined.
def convertName(text):
    text = text.lower()
    if text == 'la armor':
        return 'left_arm'
    if text == 'ra armor':
        return 'right_arm'
    if text == 'll armor':
        return 'left_leg'
    if text == 'rl armor':
        return 'right_leg'
    if text == 'lt armor':
        return 'left_torso'
    if text == 'rt armor':
        return 'right_torso'
    if text == 'ct armor':
        return 'center_torso'
    if text == 'rtl armor':
        return 'rear_left_torso'
    if text == 'rtr armor':
        return 'rear_right_torso'
    if text == 'rtc armor':
        return 'rear_center_torso'
    if text == 'hd armor':
        return 'head'
    return text

def makeDict(l):
    res = {}
    for i in l:
        res[convertName(i[0])] = i[1]
    return res

def collectObject(atr_list):
    # First collect standard key pairs.
    # Replace some key with a different key value.
    key_pairs = {'chassis': 'chassis', 'model': 'variant',
                 'config': 'config', 'techbase': 'tech_base',
                 'era': 'era', 'source': 'source', 'rules level':
                 'rules_level', 'role': 'role', 'mass': 'weight',
                 'engine': 'engine', 'structure': 'structure_type',
                 'myomer': 'myomer', }
    obj = {}
    for pair in atr_list:
        for key, value in key_pairs.items():
            if pair[0] == key:
                obj[value] = pair[1]
    # Handle quirks.
    quirks = []
    for pair in atr_list:
        if pair[0] == 'quirk':
            quirks.append(pair[1])
    obj['quirks'] = quirks
    for pair in atr_list:
        if pair[0] == 'heat sinks':
            obj['heat_sinks'] = pair[1].split()
    # Define a movement object.
    movement = {}
    for pair in atr_list:
        if pair[0] == 'walk mp':
            movement['walk'] = pair[1]
            movement['run'] = int(pair[1]) + math.ceil(int(pair[1]) / 2.0)
        if pair[0] == 'jump mp':
            movement['jump'] = pair[1]
    obj['movement'] = movement
    # Handle structure and armor.
    for pair in atr_list:
        if pair[0] == 'structure':
            obj['structure_type'] = pair[1].lower()
        if pair[0] == 'armor':
            obj['armor_type'] = pair[1]
            obj['armor'] = pair[2]
    # Create a weapons list.
    for pair in atr_list:
        if pair[0] == 'weapons':
            weapons_keys = []
            weapons_values = []
            for weapon in pair[1]:
                weapons_keys.append(weapon[1])
                weapons_values.append(weapon[0])
            obj['weapons'] = list(zip(weapons_keys, weapons_values))
    # Generate a critical hit table.
    crit_table = {}
    for pair in atr_list:
            if pair[0] == 'left arm':
                crit_table['left_arm'] = pair[1]
            elif pair[0] == 'right arm':
                crit_table['right_arm'] = pair[1]
            if pair[0] == 'left leg':
                crit_table['left_leg'] = pair[1]
            elif pair[0] == 'right leg':
                crit_table['right_leg'] = pair[1]
            if pair[0] == 'left torso':
                crit_table['left_torso'] = pair[1]
            elif pair[0] == 'right torso':
                crit_table['right_torso'] = pair[1]
            if pair[0] == 'center torso':
                crit_table['center_torso'] = pair[1]
            elif pair[0] == 'head':
                crit_table['head'] = pair[1]
    obj['critical_table'] = crit_table
    return obj
        


# First collect the path for all files to convert.
file_list = []
path_list = Path('.\mechs').glob('**/*.mtf')
for path in path_list:
    path_as_str = str(path)   
    file_list.append(path_as_str);


# Setup the sqlite database
mech_db = sqlite3.connect("mech.db")

curs = mech_db.cursor()
try:
    curs.execute("CREATE TABLE mechs(variant, chassis, data)")
except Exception as e:
    print(e)

# Iterate thought the file list.
# Document any auto corrected files.
count = 0
corrected_list = []
for i in file_list:
    # Loop through each file and get a text string of it's contents.
    mech_file = open(i, "r", encoding="utf-8")
    mech = mech_file.read()
    
    mech = mech.split('\n')
    mech_atr = initAttributes(mech)
    mech_atr = simplifyLongPairs(mech_atr)
    mech_atr = defineCriticalLocations(mech_atr)
    mech_atr = defineWeaponsList(mech_atr)
    mech_atr = defineArmorList(mech_atr)

    # Convert the text to a python dictionary.
    obj = collectObject(mech_atr)

    # print('\n')
    # print(obj)
    # print('\n')
    # break

    # Write the dictionary to the database.
    # If there is a failure, we try again by 
    # manually setting the model attribute.
    # Some clan mechs are missing that for 
    # the base model of the mech.
    try:
        try:
            curs.execute("INSERT INTO mechs VALUES(?, ?, ?)", (obj['variant'], obj['chassis'], json.dumps(obj)))
        except Exception as e:
            try:
                curs.execute("INSERT INTO mechs VALUES(?, ?, ?)", ('base', obj['chassis'], json.dumps(obj)))
                corrected_list.append(obj['chassis'])
            except Exception as e:
                # Collect the data to id the failed db write.
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
