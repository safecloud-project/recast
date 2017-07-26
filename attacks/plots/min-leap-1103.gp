set term postscript color eps enhanced 22
set output "min-leap-1103.eps"
#load "../styles.inc"

NX=1
NY=1
# Size of graphs
SX=0.72
SY=0.5

# Margins
MX=0.2
MY=0.1
# Space between graphs
IX=-0.14
IY=0.11
# Space for legends
LX=0.05
LY=0.02

set size 1,0.7

set lmargin MX+0
set rmargin MX+13

set tmargin MY+0.2
set bmargin MY+0

set multiplot

set origin MX+LX+0*(IX+SX),MY+0*(IY+SY)+LY
set size SX,SY
set grid noxtics ytics




set title "Leaping and Minimum attack"

set xlabel ""
set ylabel "Fraction of destroyed docs"
set key left bottom sample 1

set log x
set log y
set format y "10^{%+02T}";
#set xrange [2500:20000]
#set xtics ("2500" 2500, "5000" 5000, "10000" 10000, "20000" 20000) rotate by 45 right
plot '../data/dataMLAttacks1103.txt' using 1:2 with linespoints title "d_{1}" lc rgb "brown" linewidth 4.0, \
'../data/dataMLAttacks1103.txt' using 1:3 with linespoints title "d_{5}" lc rgb "violet" linewidth 4.0, \
'../data/dataMLAttacks1103.txt' using 1:4 with linespoints title "d_{50}" lc rgb "blue" linewidth 4.0, \
'../data/dataMLAttacks1103.txt' using 1:5 with linespoints title "d_{150}" lc rgb "cyan" linewidth 4.0, \
'../data/dataMLAttacks1103.txt' using 1:6 with linespoints title "d_{500}" lc rgb "red" linewidth 4.0, \
'../data/dataMLAttacks1103.txt' using 1:7 with linespoints title "d_{1000}" lc rgb "orange" linewidth 4.0, \


				
!epstopdf "min-leap-1103.eps"
!rm "min-leap-1103.eps"
quit