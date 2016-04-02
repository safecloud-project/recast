FILES=dockerenv/*

for f in $FILES
do
    ./pyeclib-encode-microbench.sh "$f" "1" "1"
done