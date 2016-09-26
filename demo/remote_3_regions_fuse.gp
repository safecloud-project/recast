set term postscript color eps enhanced 22
set output "remote_3_regions_fuse.eps"
load "styles.inc"
set size 1,0.65
set bmargin 3
set tmargin 2
set lmargin 6
set rmargin 3
set title "Remote Redis cluster, Fuse, RS (10,4)" offset 0,-0.5
set ylabel "Latency (sec)"
set xlabel "Requests"
set grid y
#set logscale y
#set ytics 0,20,100
set yrange [0.01:8]
set xrange [0:60]
set key horizontal samplen 1 width 1 at 32,7.9

set label 1001 "CH" at 9, 4
set label 1003 "US" at 29, 5
set label 1002 "SG" at 49, 6

plot \
	'data/4194304_data.txt'  u ($1):($3)\
		 w l ls 8 notitle '4MB',\
	'data/4194304_data.txt'  u ($1):($3) every 2\
		 w p ls 8 notitle '4MB',\
   	10000\
 		w lp ls 8 notitle '4MB'		
	

!epstopdf "remote_3_regions_fuse.eps"
!rm "remote_3_regions_fuse.eps"
quit
