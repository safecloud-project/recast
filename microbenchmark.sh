FILES=env/*

for f in $FILES
do
    ./pyeclib-encode-microbench.sh "$f" "10" 100"
done