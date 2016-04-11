FILES=dockerenv/*/*

REPETITIONS=1
REQUESTS=1
for f in $FILES
do
    # repetitions
    # requests
    ./pyeclib-encode-microbench.sh "$f" $REPETITIONS $REQUESTS
done

#for f in $FILES
#do
    # repetitions
    # requests
#    ./pyeclib-decode-microbench.sh "$f" $REPETITIONS $REQUESTS
#done
