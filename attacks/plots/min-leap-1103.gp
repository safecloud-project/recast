set term postscript color eps enhanced 22
set output "min-leap-1103.eps"
#load "../styles.inc"


set size 1,0.8

set lmargin 8
set rmargin 3

set tmargin 2.2
set bmargin 3.2

set multiplot

set grid noxtics ytics

set title "Leaping attack"

set xlabel "# archived documents"
set ylabel "Fraction of destroyed docs"
set key left bottom horizontal sample 1

set log x
set log y
set format y "10^{%+02T}";
#set xrange [2500:20000]
#set xtics ("2500" 2500, "5000" 5000, "10000" 10000, "20000" 20000) rotate by 45 right
plot 'data/dataMLAttacks1103.txt' using 1:2 with linespoints title "d_{1}" lc rgb "brown" linewidth 4.0, \
'data/dataMLAttacks1103.txt' using 1:3 with linespoints title "d_{5}" lc rgb "red" linewidth 4.0, \
'data/dataMLAttacks1103.txt' using 1:4 with linespoints title "d_{50}" lc rgb "blue" linewidth 4.0, \
'data/dataMLAttacks1103.txt' using 1:5 with linespoints title "d_{150}" lc rgb "cyan" linewidth 4.0, \
'data/dataMLAttacks1103.txt' using 1:6 with linespoints title "d_{500}" lc rgb "violet" linewidth 4.0, \


				
!epstopdf "min-leap-1103.eps"
!rm "min-leap-1103.eps"
quit