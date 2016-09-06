#!/bin/bash
demo='local_nodes'
api='http'
input_file="$demo/$api.log"
requests=`wc -l $input_file | awk -F ' ' {'print $1'}`

rm data/*
gnuplot ${demo}_${api}.gp

for (( i = 1; i <= $requests; i++ )); do
	echo "Reading $i lines"
	head -n $i $input_file > tmp_gnuplot_input
	bash split.sh tmp_gnuplot_input
	gnuplot ${demo}_${api}.gp
	sleep 0.25;
done