# Gather raw data into the two files used by the plotting script
!cat remote_clusterinfo/fuse.log remote_north_virginia/fuse.log remote_singapore/fuse.log | nl > data/fuse.log
!cat remote_clusterinfo/http.log remote_north_virginia/http.log remote_singapore/http.log | nl > data/http.log
# Plot
set term postscript color eps enhanced 22
set output "remote_3_regions.eps"
load "styles.inc"
set size 1,0.65
set bmargin 3
set tmargin 2
set lmargin 6
set rmargin 3
set title "Storing 4MB files in a 3 remote nodes RS (10,4)" offset 0,-0.5
set ylabel "Latency (sec)"
set xlabel "Requests"
set grid y
set yrange [0.01:6]
set xrange [0:60]

set label 1001 "CH" at  9, 3
set label 1003 "US" at 29, 4
set label 1002 "SG" at 49, 5

plot \
	'data/http.log' using ($1):($3) with line linestyle 7 notitle 'http',\
	'data/http.log' using ($1):($3) with points linestyle 7 notitle 'http',\
	'data/fuse.log' using ($1):($3) with line linestyle 5 notitle 'fuse',\
	'data/fuse.log' using ($1):($3) with points linestyle 5 notitle 'fuse'

!epstopdf "remote_3_regions.eps"
!rm "remote_3_regions.eps"
quit
