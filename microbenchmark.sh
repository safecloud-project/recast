FILES=env/*

for f in $FILES
do
    ./pyeclib-encode-microbench $f 10 100
done