FILES=dockerenv/*

for f in $FILES
do
    # repetitions
    # requests
    ./pyeclib-encode-microbench.sh "$f" "1" "100"
done