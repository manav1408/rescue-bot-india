import json
import re
import pickle
import os

FILENAME = "userdata.p"

def extract_numbers(num_str):
    #extracts all the phone numbers from num_str
    print 'Inside extract numbers method'
    phone_numbers = []
    temp = re.findall(r'\d+', num_str)
    for num in temp:
        if len(num)==10:
            phone_numbers.append(num)
        if len(num)==11 and num[0]==0:
            phone_numbers.append(num[1:])
    return phone_numbers

def save_numbers(uid,num_str):
    #num_str expects a string containing contact numbers
    print 'Inside save numbers method'
    contact_numbers = extract_numbers(num_str)
    user_number = contact_numbers[0]
    user_emergency_numbers = contact_numbers[1:]
    old_map = {}
    try:
        fileObject = open(FILENAME, 'rb')
        old_map = pickle.load(fileObject)
        fileObject.close()
    except:
        pass
    fileObject = open(FILENAME,'wb')
    if old_map.get(str(uid)):
        old_map[str(uid)] = 	{
								'user_number' : user_number,
								'emergency_numbers' : user_emergency_numbers
    							}
    else:
        old_map[str(uid)] = {}
        old_map[str(uid)] = 	{
								'user_number' : user_number,
								'emergency_numbers' : user_emergency_numbers
    							}
    pickle.dump(old_map,fileObject)
    fileObject.close()

def get_user_numbers(uid):
    print 'Inside get user numbers method'
    results = {}
    try:
        fileObject = open(FILENAME,'rb')
        results = pickle.load(fileObject)
        fileObject.close()
    except (OSError, IOError) as e:
        print "No data found, creating new file"
        os.mknod(FILENAME)
        pickle.dump(results, open(FILENAME, "wb"))
    return results.get(str(uid))

# save_numbers('u1','My number is 8447370864, cousin number is 7756987412 and other numbers are 6666666666,1234567890')
# get_user_numbers('u1')