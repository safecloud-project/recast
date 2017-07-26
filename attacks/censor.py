import Tkinter as tk
import pickle
import sys
import attack_pattern as ap
import time

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

if len(sys.argv) != 8:
    print_usage()
    sys.exit(0)

print "Requires file naming 'rand%d.txt'.\n"
# Check files   
##var = raw_input("Did you respect the format rand%d.txt of naming? (y/n) ")
##if (var == "n"):
##    sys.exit("PLEASE CALL THE FILES 'rand%d.txt'.")
##elif (var == "y"):
##    pass
##else:
##    sys.exit("Please answer either yes or no.")

# Target document and heuristic
heuristic = sys.argv[6]

# Choose dictionary
#import dictionary1103n30000 as dictionary
#Dict = dictionary.dictionary
#save_obj(Dict, 'dictionaries/dictionary1103n30000')
Dict = load_obj('dictionaries/dict')

NUM_DOCS = int(sys.argv[2]) # For NUM_DOCS < len(Dict.keys())) we select a subset
if (NUM_DOCS > len(Dict.keys())):
    sys.exit("Dictionary dimension mismatch.")

# Set parameters
num_source  = int(sys.argv[3]) #2#1
num_pointer = int(sys.argv[4]) #7#10 # t = Number of pointers
num_parity = int(sys.argv[5]) #5#3
e = num_parity - num_source # correction capability
NDIGIT = 2 # Number of digits for the block index in files names

# Sort keys according to timestamps
KEYS = ["rand%d.txt"%i for i in range(NUM_DOCS)] 
    
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

if (sys.argv[7] != "draw"):
    # Run the attack
    if ((heuristic == "MinimumAttack") or (heuristic == "LeapingAttack") or (heuristic == "CreepingAttack") or (heuristic == "TailoredAttack")):
        target_doc = "rand%d.txt" % int(sys.argv[1])
        B = ap.greedy_attack(heuristic, target_doc, num_pointer, e, num_parity, POINTERDICT, NUM_DOCS)
    elif (heuristic == "KillNodes"):
        percentage = float(sys.argv[1])
        BLOCKSTONODES = ap.blocks_to_nodes(Dict, KEYS, num_parity)
        B = ap.kill_random_nodes(BLOCKSTONODES, percentage)
    elif (heuristic == "KillDocs"):
        percentage = float(sys.argv[1])
        blocks_per_doc = e # how many pointer blocks per doc to erase
        B = ap.kill_random_docs(NUM_DOCS, percentage, blocks_per_doc, num_parity)
    elif (heuristic == "KillRand"):
        percentage = float(sys.argv[1])
        B = ap.kill_random(NUM_DOCS, percentage, num_parity)
    else:
        sys.exit("censor.py: unknown heuristic (*)")

    filea = open("blocks-to-erase.txt", "a")
    for i in range(len(B)):
        filea.write("%s\n"% B[i])
    filea.close()
    
else:

    CANVAS_SIZE = 1000 # Canvas size
    RADIUS = CANVAS_SIZE/NUM_DOCS/2 # Radius of the balls in the canvas
    if (RADIUS < 1):
        RADIUS = 1
        
    POS = {} # Dictionary for coordinates of balls in the canvas (parity only)
    POSPOINTERS = {} # Coordinates of pointers
    EDGES = [] # i is the tag of the edge, a, b tags for the nodes

    # Set up the canvas
    #global root
    root = tk.Tk()
    w = tk.Canvas(root, width=RADIUS*2*(num_parity+num_pointer+1), height=CANVAS_SIZE)

    # Dictionaries
    poscount = 0 # Y-coordinate of balls (it is constant fixed a document)
    myrange = range(RADIUS,RADIUS*2*(num_parity+num_pointer),RADIUS*2) # X-coordinates of balls

    for k in KEYS:
        for i in range(num_parity):
            POS[k+"-"+str(i).zfill(NDIGIT)] = [myrange[i+num_pointer],poscount]

        j = 0
        tempv = []
        for p in POINTERDICT[k]:
            tempv = tempv + [ [p, myrange[j],poscount] ]
            j = j + 1

        POSPOINTERS[k] = tempv
        poscount = poscount + RADIUS*1.5

    # Dictionary that describes which blocks are hosted in which nodes
    # Nodes ids are the keys of the dictionary
    BLOCKSTONODES = ap.blocks_to_nodes(Dict, KEYS, num_parity)

    # Place edges
    for k in KEYS:
        for triple in POSPOINTERS[k]:
            posa = [triple[1], triple[2]] # Pointer block

            b = triple[0]
            posb = POS[b] # SOurce block
            w.create_line(posb[0]+RADIUS, posb[1]+RADIUS, posa[0]+RADIUS, posa[1]+RADIUS, arrow=tk.FIRST, tag = k+"-edge-"+b)
            EDGES.append([k+"-edge-"+b, [posb, posa]])       

    # Place the pointers
    for k in KEYS:
        for triple in POSPOINTERS[k]:
            pos = [triple[1], triple[2]] # Pointer block
            w.create_oval(pos[0], pos[1], pos[0]+2*(RADIUS-(RADIUS/4)), pos[1]+2*(RADIUS-(RADIUS/4)), fill="green", stipple='gray12', dash=(3,5), tags = k+"-pointer-"+triple[0])

    def callback(event):
        tags = event.widget.gettags("current") #print "clicked at", event.x, event.y
           
        w.itemconfig(tags[0], fill="orange")

        for d in EDGES:           
            if (tags[0] in d[0]):
                w.itemconfig(d[0], fill="orange")
                block = d[0].replace("-edge-",""); block = block.replace(tags[0],"");
                #print "block = ", block
                w.itemconfig(block, fill="orange")

                # Paint the pointer block
                mytag = d[0]
                mytag = mytag.replace("pointer-", ""); mytag = mytag.replace("-edge-", "")
                mytag = "pointer-" + mytag[0:len(mytag)/2]
                w.itemconfig(mytag, fill="orange")

    # Place the nodes
    for k in POS.keys():   
        pos = POS[k]
        # http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/create_oval.html
        if not ("pointer" in k):
            w.create_oval(pos[0], pos[1], pos[0]+2*(RADIUS-(RADIUS/4)), pos[1]+2*(RADIUS-(RADIUS/4)), fill="green", tags = k)
            w.tag_bind(k, '<ButtonPress-1>', callback) # click on parity not on pointers
            
    try :
        if ((heuristic == "KillNodes") or (heuristic == "KillDocs") or (heuristic == "KillRand")):
            percentage = float(sys.argv[1])
            blocks_per_doc = e
            if (heuristic == "KillNodes"):
                ap.draw_random(heuristic, NUM_DOCS, percentage, blocks_per_doc, num_parity, EDGES, w, BLOCKSTONODES)
            else:
                ap.draw_random(heuristic, NUM_DOCS, percentage, blocks_per_doc, num_parity, EDGES, w)          
    except IndexError:
        pass

   
    try :
        if ((heuristic == "MinimumAttack") or (heuristic == "LeapingAttack") or (heuristic == "CreepingAttack") or (heuristic == "TailoredAttack")):
            target_doc = "rand%d.txt" % int(sys.argv[1])
            ap.draw_greedy(heuristic, w, EDGES, target_doc, num_pointer, num_parity-num_source, num_parity, POINTERDICT, NUM_DOCS )
    except IndexError:
        pass

    # Start the event loop
    w.pack()
    root.mainloop()
                

