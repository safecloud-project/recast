FILES=dockerenv/*

for f in $FILES
do
    # repetitions
    # requests
    ./pyeclib-encode-microbench.sh "$f" "10" "100"
done