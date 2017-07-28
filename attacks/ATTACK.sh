NUMFILES=200

rm blocks-to-erase/*
python dump_graph.py

array=(1 50 150) # 500 1000)
for i in "${array[@]}" 
do
	# num_docs s t p draw heuristic target_doc heuristic target_doc
	python main.py $NUMFILES 1 10 3 ndraw MinimumAttack $i LeapingAttack $i CreepingAttack $i TailoredAttack $i
done

array=(0.01 0.05 0.1)
for i in "${array[@]}" 
do
	# num_docs s t p draw heuristic percentage heuristic percentage
	python main.py $NUMFILES 1 10 3 ndraw KillNodes $i KillRand $i KillDocs $i
done



