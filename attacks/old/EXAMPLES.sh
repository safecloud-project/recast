python censor.py 0.1 100 1 10 3 KillDocs nodraw # percentage num_docs s t p heuristic draw

python censor.py 0.1 100 1 10 3 KillNodes draw 

python censor.py 0.1 100 1 10 3 KillRand nodraw 

# --------------------------------------------------------------------

python censor.py 50 1000 1 10 3 MinimumAttack nodraw # target_file num_docs s t p heuristic draw

python censor.py 50 1000 1 10 3 LeapingAttack nodraw # target_file num_docs s t p heuristic draw

python censor.py 50 1000 1 10 3 CreepingAttack nodraw # s t p

python censor.py 50 1000 1 10 3 TailoredAttack nodraw # s t p