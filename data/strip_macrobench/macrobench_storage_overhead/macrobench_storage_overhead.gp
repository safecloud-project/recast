set term post color eps 22 enhanced
set output "macrobench_storage_overhead.eps"
load "../../../papers/DAIS-2016/plots/styles.inc"
set size 1,0.65
set lmargin 10
set rmargin 2
set tmargin 3
set bmargin 4.5
set grid noxtics ytics
set style histogram gap 1
set style data histograms
set ylabel "Normalized\nStorage Overhead"
set style fill solid 1.00 border 0
set boxwidth 0.9
set yrange[100:160]#3345779097.5
#set xrange [0.5:]
#set ytics ("1GB" 1048593032.5, "2GB" 2097186065, "3GB" 3145779097.5) # "2.5GB" 2621482581.25,
set ytics ("0%%" 100,"+10%%" 110,"+20%%" 120,"+30%%" 130,"+40%%" 140,"+50%%" 150,"+60%%" 160)
set xtics rotate by -35 font "Arial,16"
set key horizontal outside sample 0.1
set title "500 <key,value> pairs, key=128bit, value=4MB"

set label 1001 "2GB" at  -0.2,106  font "Helvetica,12" front
set label 1002 "2.93GB" at 0.7,144 font "Helvetica,12" front
set label 1003 "2.95GB" at 1.7,144 font "Helvetica,12" front
set label 1004 "2.93GB" at 2.7,144 font "Helvetica,12" front
set label 1005 "3.14GB" at 3.7,154 font "Helvetica,12" front
set label 1006 "3.14GB" at 4.7,154 font "Helvetica,12" front
set label 1007 "2.93GB" at 5.7,144 font "Helvetica,12" front
set label 1008 "2.93GB" at 6.7,144 font "Helvetica,12" front
#
plot "data/overhead.txt" u ($3):xtic(1) ls 1 notitle "4 MB"

!epstopdf "macrobench_storage_overhead.eps"
!rm "macrobench_storage_overhead.eps"
quit
