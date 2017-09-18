#! /usr/bin/env gnuplot
set term pdfcairo enhanced
set output "traffic.pdf"

set title "Coder traffic while reconstructing with STeP(1, 10, 3)"
set xlabel "Blocks to reconstruct"
set ylabel "Data transferred (kB)"

set key box inside top left
#set nokey

set style histogram errorbars gap 1 linewidth 1
set style data histogram
set style fill solid noborder

set grid noxtics ytics
set ytics 100

set datafile separator ","
plot "./data/bw.csv" using 2:3:xticlabels(1) linecolor rgb("#FF4500") title columnheader(2),\
     "./data/bw.csv" using 4:5:xticlabels(1) linecolor rgb("#32CD32") title columnheader(4)
quit