FILES=dockerenv/*

REPETITIONS=10
REQUESTS=1000
for f in $FILES
do
    # repetitions
    # requests
    ./pyeclib-encode-microbench.sh "$f" $REPETITIONS $REQUESTS
done

for f in $FILES
do
    # repetitions
    # requests
    ./pyeclib-decode-microbench.sh "$f" $REPETITIONS $REPETITIONS
done
