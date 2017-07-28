import pickle
import sys
import time
import datetime
import censor

NDIGIT = 2 # Number of digits for the block index in files names

def save_obj(a, name ):
    with open(name + '.pickle', 'wb') as handle:
        return pickle.dump(a, handle, protocol=pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    with open(name + '.pickle', 'rb') as handle:
        return pickle.load(handle)
    
def print_usage():
    """Prints the usage message"""
    print "Censor a document\n"
    print "Use: python censor.py x NUM_DOCS s t p heuristic flag\n"
    print "Arguments:"
    print "\tif Greedy, x = index of the target document to censor (0 <= x < NUM_DOCS)\n\tif KillNodes, x = percentage of nodes to be shut down (0 < x < 1)\n"
    print "\tNUM_DOCS = total number of docs in the archive\n"
    print "\ts = number of source blocks\n"
    print "\tt = number of pointer blocks\n"
    print "\tp = number of parity blocks\n"
    print "\theuristic = MinimumAttack or LeapingAttack or CreepingAttack or TailoredAttack or KillNodes or KillDocs or KillRand\n"
    print "\tflag = write 'draw' if you want graphical visualization\n"

if len(sys.argv) < 8:
    print_usage()
    sys.exit(0)

# Choose dictionary
#import dictio as dictionary
#Dict = dictionary.dictionary
#save_obj(Dict, 'dictionaries/dictionary1103n30000')
Dict = load_obj('dictionaries/dict')

# Set parameters
num_source  = int(sys.argv[2]) #2#1
num_pointer = int(sys.argv[3]) #7#10 # t = Number of pointers
num_parity = int(sys.argv[4]) #5#3
draw = sys.argv[5]

NUM_DOCS = int(sys.argv[1]) # For NUM_DOCS < len(Dict.keys())) we select a subset
if (NUM_DOCS > len(Dict.keys())):
    sys.exit("Dictionary dimension mismatch.")

# Sort keys according to timestamps
timestamps = [Dict[k][0] for k in Dict.keys()]
dates = [datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S.%f") for ts in timestamps]
dates.sort()
sorteddates = [datetime.datetime.strftime(ts, "%Y-%m-%d %H:%M:%S.%f") for ts in dates]
sorteddates = sorteddates[0:NUM_DOCS]

KEYS = [0]*NUM_DOCS
for i in range(NUM_DOCS):
    for k in Dict.keys():
        if (Dict[k][0] == sorteddates[i]):
            KEYS[i] = k
            break
    
# Prepare dictionary POINTERDICT
# It will have as many entries as files in the archive
# The key of the entry is the name of the archived file
# The value is an array of strings which represent the
# pointers blocks of the doc identified by the key.
POINTERDICT = {} # Dictionary storing blocks pointed to by the doc identified by the key
counter = 0
for k in KEYS: 
    entry = Dict[k]
    index = []
    filename = []
    count = 0
    for s in entry[1].split():
        r = s
        r = r.replace("[",""); r = r.replace("]","")
        r = r.replace(",",""); r = r.replace('"',"")
        if (count % 2 == 0):
            filename.append(r)
        else:
            index.append(int(r))
        count = count + 1
    
    if index != []:
        if (counter < num_pointer):
            POINTERDICT[k] = [filename[i]+"-"+str(index[i]).zfill(NDIGIT) for i in range(counter)]
        else:
            POINTERDICT[k] = [filename[i]+"-"+str(index[i]).zfill(NDIGIT) for i in range(num_pointer)]
    else:
        POINTERDICT[k] = []

    counter = counter + 1

print "I'm done with the dictionary."



heuristic = sys.argv[6]
TDP = sys.argv[7] # target document or percentage

censor.censor(heuristic, TDP, Dict, KEYS, NUM_DOCS, POINTERDICT, num_source, num_pointer, num_parity, draw)

for i in range(8,len(sys.argv),2):
    heuristic = sys.argv[i]
    TDP = sys.argv[i+1] # target document or percentage
    censor.censor(heuristic, TDP, Dict, KEYS, NUM_DOCS, POINTERDICT, num_source, num_pointer, num_parity, draw)
