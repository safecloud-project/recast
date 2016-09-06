#!/bin/bash
input_file='fuse_used.log'
requests=`wc -l $input_file | awk -F ' ' {'print $1'}`

rm data/*
gnuplot demo_local_fuse.gp

for (( i = 1; i < $requests; i++ )); do
	echo "Reading $i lines"
	head -n $i $input_file > tmp_gnuplot_input
	bash split.sh tmp_gnuplot_input
	gnuplot demo_local_fuse.gp
	sleep 0.25;
done