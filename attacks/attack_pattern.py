import random
import sys

NDIGIT = 2 # Number of digits for the block index in files names

def blocks_to_nodes(Dict, KEYS, p):
    # Dictionary that describes which blocks are hosted in which nodes
    # Nodes ids are the keys of the dictionary

    BLOCKSTONODES = {}
    for k in KEYS:

        mylist = Dict[k][2].split()

        count = 0
        for s in mylist:
            if (count % 2 == 0):
                s = s.replace("[",""); s = s.replace("]","")
                s = s.replace(",",""); s = s.replace('"',""); s = s.replace("'","")
                if (NDIGIT == 2 and p < 10):
                    s = s.replace("-","-0")
                elif (NDIGIT == 2 and p >= 10 and p < 100):
                    pass
                else :
                    sys.exit("Change NDIGIT!!")
                    
                block = s

            else:            
                s = s.replace("]",""); s = s.replace("'",""); s = s.replace(",","")
                if (NDIGIT == 2 and p < 10):
                    s = s.replace("-","-0")
                elif (NDIGIT == 2 and p >= 10 and p < 100):
                    pass
                else :
                    sys.exit("Change NDIGIT!!")
                    
                try:
                    BLOCKSTONODES[s].append(block)
                except KeyError:
                    BLOCKSTONODES[s] = [block]
                        
            count = count + 1

    return BLOCKSTONODES


def kill_random_nodes(BLOCKSTONODES, percentage):
    " Output the list of lost blocks "
    # percentage: float in [0,1] ex. 0.4 = 40%
    # w is the canvas
    
    NUMNODES = len(BLOCKSTONODES.keys())
    num_down_nodes = int(NUMNODES * percentage)
    
    down_nodes = random.sample(BLOCKSTONODES.keys(), num_down_nodes)
    
    LOSTBLOCKS = []
    for n in down_nodes:
        LOSTBLOCKS.extend(BLOCKSTONODES[n])
    
    return LOSTBLOCKS

def kill_random_docs(NUM_DOCS, percentage, blocks_per_doc, p):
    " Output the list of lost blocks "
    # percentage: float in [0,1] ex. 0.4 = 40%
    # blocks_per_doc : how many pointer blocks per doc to erase
    # w is the canvas
    
    num_down_docs = int(NUM_DOCS * percentage)
    
    down_docs = random.sample(range(NUM_DOCS), num_down_docs)

    LOSTBLOCKS = []
    for n in down_docs:
        indices = [str(i).zfill(NDIGIT) for i in random.sample(range(p), blocks_per_doc)]
        LOSTBLOCKS = LOSTBLOCKS + ["rand%d"%n+".txt-%s"%i for i in indices]
    
    return LOSTBLOCKS

def kill_random(NUM_DOCS, percentage, p):
    " Output the list of lost blocks "
    # percentage: float in [0,1] ex. 0.4 = 40%
    # blocks_per_doc : how many pointer blocks per doc to erase
    # w is the canvas
    
    num_down_blocks = int(NUM_DOCS * percentage * p)

    LOSTBLOCKS = [0]*num_down_blocks
    count = 0
    while count < num_down_blocks:
        doc_idx = random.choice(range(NUM_DOCS))
        block_idx = str(random.choice(range(p))).zfill(NDIGIT) 
        LOSTBLOCKS[count] = "rand%d"%doc_idx+".txt-%s"%block_idx
        count = count + 1

    LOSTBLOCKS = set(LOSTBLOCKS)
    while len(LOSTBLOCKS) < num_down_blocks:
        doc_idx = random.choice(range(NUM_DOCS))
        block_idx = str(random.choice(range(p))).zfill(NDIGIT) 
        LOSTBLOCKS.add( "rand%d"%doc_idx+".txt-%s"%block_idx )
        
    return LOSTBLOCKS

def draw_random(heuristic, NUM_DOCS, percentage, blocks_per_doc, p, EDGES, w, BLOCKSTONODES = None):
    if (heuristic == "KillNodes"):
        LOSTBLOCKS = kill_random_nodes(BLOCKSTONODES, percentage)
    elif (heuristic == "KillDocs"):
        LOSTBLOCKS = kill_random_docs(NUM_DOCS, percentage, blocks_per_doc, p)
    elif (heuristic == "KillRand"):
        LOSTBLOCKS = kill_random(NUM_DOCS, percentage, p)
    else:
        sys.exit("Unknown heuristic. (#)")

    for b in LOSTBLOCKS: # paint parity blocks
        w.itemconfig(b, fill = "red") # target doc

        for d in EDGES: # paint edges and pointer blocks          
            if (b in d[0]):
                #print "d = ", b, d[0]
                tag = d[0]
                w.itemconfig(tag, state = "hidden")
                w.itemconfig(tag.replace("-edge-", "-pointer-"), fill = "orange")

                
    
############ ------------- Let's GREEDY ------------- ############ 
NDIGIT = 2 # Number of digits for the block index in files names

def count_blocks(doc, set_blocks, p, POINTERDICT):
    "This function counts how many blocks of document doc are in the set set_blocks"
    
    count = 0
    for i in range(p): # Check the parity blocks
        if (doc+"-"+str(i).zfill(NDIGIT) in set_blocks):
            count = count + 1
    for b in POINTERDICT[doc]: # Check the pointer blocks
        if (b in set_blocks):
            count = count + 1
    return count

def documents(block, POINTERDICT):
    "Compute the set of documents with block as block"
    
    bset = [block[:-(NDIGIT+1)]] # block is part of 1 doc as parity block
    
    index = bset[0]; index = index.replace("rand",""); index = index.replace(".txt","")
    for i in range(int(index), len(POINTERDICT.keys())): # seek of which docs block is part as pointer block
        k = "rand%d.txt"%i
        if (block in POINTERDICT[k]):
            bset = bset + [k]
    return bset

def mymin(docsset):
    # Return the minimal index of the documents in the set docsset
    indices = [0]*len(docsset)
    for i in range(len(docsset)):
        b = docsset[i]; b = b.replace("rand",""); b = b.replace(".txt","")
        indices[i] = int(b)
    return min(indices)

def mymax(docsset):
    # Return the maximal index of the documents in the set docsset
    indices = [0]*len(docsset)
    for i in range(len(docsset)):
        b = docsset[i]; b = b.replace("rand",""); b = b.replace(".txt","")
        indices[i] = int(b)
    return max(indices)

def CreepingAttack(C, b, POINTERDICT):
    C1 = list(set(C + documents(b, POINTERDICT)))
    return mymax(C1) - mymin(C1)

def MinimumAttack(C, b, POINTERDICT):
    return len( list(set(C+documents(b, POINTERDICT))) )

def LeapingAttack(C, b, POINTERDICT):
    N = documents(b, POINTERDICT)
    for c in C:
        if (c in N):
            N.remove(c)

    if (N == []):
        return -float("inf")
    else:
        return 0 - mymin(N)

def blocks(doc, p, POINTERDICT):
    "Compute the set of blocks of document doc."
    # p: number of parity blocks
    bs = POINTERDICT[doc]
    bs = bs + [doc+"-"+str(i).zfill(NDIGIT) for i in range(p)]
    return bs

def TailoredAttack(C, B, b, POINTERDICT, t, e, p, K):
    import math
    cost = 0
    B1 = B + [b]
    C1 = list(set(C + documents(b, POINTERDICT)))
    for c in C1:
        inter = set(B1).intersection(blocks(c, p, POINTERDICT))
        yettoerase = max( [0 , e + 1 - len(inter)] )
        ci = c.replace("rand",""); ci = ci.replace(".txt",""); ci = int(ci)
        cost = cost + 1 + yettoerase*t*math.log( 1+ (K-ci)/ci )

    return cost

def greedy_attack(heuristic, target_doc, t, e, p, POINTERDICT, NUM_DOCS):
    "Greedy attack framework."
    # heuristic : one of MinimumAttack, LeapingAttack, CreepingAttack, TailoredAttack
    # target_doc : complete name of the doc to be erased
    # t : number of pointer blocks
    # e : erasure decoding capability of the code (e = p-s)
    # p : number of parity blocks
    # POINTERDICT : dictionary storing blocks pointed to by the doc identified by the key
    # NUM_DOCS : total number of archived docs
    #
    # @OUTPUT: list of erased blocks
    
    R = [target_doc]
    C = [target_doc]
    B = []

    while (R != []) :
        r = "rand%d.txt"%mymin(R) # chronological order
        while (count_blocks(r, B, p, POINTERDICT) < (e+1)):
            score = {}
            for b in range(p):
                theblock = r+"-"+str(b).zfill(NDIGIT) 
                
                if (theblock not in B):
                    if (heuristic == "MinimumAttack"):
                        score[theblock] = MinimumAttack(C, theblock , POINTERDICT)
                    elif (heuristic == "LeapingAttack"):
                        score[theblock] = LeapingAttack(C, theblock , POINTERDICT)
                    elif (heuristic == "CreepingAttack"):
                        score[theblock] = CreepingAttack(C, theblock , POINTERDICT)
                    elif (heuristic == "TailoredAttack"):
                        score[theblock] = TailoredAttack(C, B, theblock, POINTERDICT, t, e, p, NUM_DOCS)
                    else:
                        print "UNKNOWN HEURISTIC.\n"
                        return 0
                    
            b = min(score, key=score.get) # b = arg min score[b]
            B = B + [b]
            docs = documents(b, POINTERDICT)
            docsC = docs[:]
            for d in C:
                if (d in docsC):
                    docsC.remove(d)
            R = R + docsC
            C = list(set(C + docs))
            
        R.remove(r)

    # COUNT THE NUMBER CORRUPTED BLOCKS PER DOC TO CHECK
    CHECK = {}
    for b in B:
        c = b[:-3]
        try:           
            CHECK[c] = CHECK[c] + 1
        except KeyError:
            CHECK[c] = 1
          
    damaged_docs = [k for k in CHECK.keys()]
    for k in CHECK.keys():
        pointers = POINTERDICT[k]
        pointers_doc = [u[:-3] for u in pointers]
        for p in pointers_doc:
            if p in damaged_docs:
                CHECK[k] = CHECK[k] + 1

    for k in CHECK.keys():
        if not (CHECK[k] >=(e+1)):
            sys.exit("The attack was not successful.")

    print "Successfull %s! %d - %s - fraction of erased docs: %f" % (heuristic, NUM_DOCS, target_doc, float(len(C))/NUM_DOCS)
    return B
            

def draw_greedy(heuristic, w, EDGES, target_doc, t, e, p, POINTERDICT, NUM_DOCS):
    '''Given a canvas w, the methods visualise the effects of the greedy attack heuristic:
    the target document is represented in red and the corrupted documents in orange.
    '''
    # heuristic: MinimumAttack or LeapingAttack or CreepingAttack or TailoredAttack
    # w: the canvas
    # EDGES: dictionary for edges of the graph
    # target_doc: name of the target document
    # t: number of pointers
    # e: correction capability of the archive (e = p-s)
    # p: number of parities
    # POINTERDICT: dictionary storing blocks pointed to by the doc identified by the key
    # NUM_DOCS: total number of archived documents
    
    LOSTBLOCKS = greedy_attack(heuristic, target_doc, t, e, p, POINTERDICT, NUM_DOCS)
    for b in LOSTBLOCKS: # paint parity blocks
        if (target_doc in b):
            w.itemconfig(b, fill = "red") # target doc
        else:
            w.itemconfig(b, fill = "orange") # corrupted doc

        for d in EDGES: # paint edges and pointer blocks          
            if (b in d[0]):
                #print "d = ", b, d[0]
                tag = d[0]
                w.itemconfig(tag, state = "hidden")
                w.itemconfig(tag.replace("-edge-", "-pointer-"), fill = "orange")
    
    return LOSTBLOCKS

