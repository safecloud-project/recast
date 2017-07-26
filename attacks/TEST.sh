NUMFILES=10000
array=(1 50 150 500)

for i in "${array[@]}" 
do
	python censor.py $i $NUMFILES 1 10 3 LeapingAttack nodraw # s t p
done

echo ""


for i in "${array[@]}" 
do
	python censor.py $i $NUMFILES 1 10 3 MinimumAttack nodraw # s t p
done
