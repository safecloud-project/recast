import sys
import attack_pattern as ap

NDIGIT = 2 # Number of digits for the block index in files names

def censor(heuristic, TDP, Dict, KEYS, NUM_DOCS, POINTERDICT, num_source, num_pointer, num_parity, draw):
    # TDP: target document or percentage
    
    e = num_parity - num_source # correction capability
    
    if (draw != "draw"):
        # Run the attack
        if ((heuristic == "MinimumAttack") or (heuristic == "LeapingAttack") or (heuristic == "CreepingAttack") or (heuristic == "TailoredAttack")):
            target_doc = KEYS[int(TDP)]
            B = ap.greedy_attack(heuristic, target_doc, num_pointer, e, num_parity, POINTERDICT, NUM_DOCS, KEYS)
        elif (heuristic == "KillNodes"):
            percentage = float(TDP)
            BLOCKSTONODES = ap.blocks_to_nodes(Dict, KEYS, num_parity)
            B = ap.kill_random_nodes(BLOCKSTONODES, percentage)
        elif (heuristic == "KillDocs"):
            percentage = float(TDP)
            blocks_per_doc = e # how many pointer blocks per doc to erase
            B = ap.kill_random_docs(NUM_DOCS, percentage, blocks_per_doc, num_parity, KEYS)
        elif (heuristic == "KillRand"):
            percentage = float(TDP)
            B = ap.kill_random(NUM_DOCS, percentage, num_parity, KEYS)
        else:
            sys.exit("censor.py: unknown heuristic (*)")

        filea = open("blocks-to-erase/bte-%s-%s.txt"%(heuristic,TDP), "a")
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
        poscount = RADIUS/2.0 # Y-coordinate of balls (it is constant fixed a document)
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
            poscount = poscount + RADIUS*2

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
                percentage = float(TDP)
                blocks_per_doc = e
                if (heuristic == "KillNodes"):
                    ap.draw_random(heuristic, NUM_DOCS, percentage, blocks_per_doc, num_parity, EDGES, w, None, BLOCKSTONODES)
                else:
                    ap.draw_random(heuristic, NUM_DOCS, percentage, blocks_per_doc, num_parity, EDGES, w, KEYS)          
        except IndexError:
            pass

       
        try :
            if ((heuristic == "MinimumAttack") or (heuristic == "LeapingAttack") or (heuristic == "CreepingAttack") or (heuristic == "TailoredAttack")):
                target_doc = KEYS[int(TDP)]
                ap.draw_greedy(heuristic, w, EDGES, target_doc, num_pointer, num_parity-num_source, num_parity, POINTERDICT, NUM_DOCS, KEYS)
        except IndexError:
            pass

        # Start the event loop
        w.pack()
        root.mainloop()
                    

