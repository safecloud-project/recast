NUMFILES=300
array=(1 50 150)

for i in "${array[@]}" 
do
	rm blocks-to-erase.txt
	python dump_graph.py
	python censor.py $i $NUMFILES 1 10 3 LeapingAttack nodraw # s t p
done

echo ""


#for i in "${array[@]}" 
#do
#	rm blocks-to-erase.txt
#	python censor.py $i $NUMFILES 1 10 3 MinimumAttack nodraw # s t p
#done
