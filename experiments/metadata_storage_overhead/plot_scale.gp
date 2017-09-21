#! /usr/bin/env gnuplot
set terminal pdfcairo enhanced
set output "mso.pdf"

set title "Metadata size over time"
set xlabel "Number of documents"
set ylabel "Size (in MB)"

set xtics rotate 90

set grid ytics

set key inside top left box

set datafile separator ","
plot "./data/mso.csv" using 2:xticlabels(1) with linespoints title columnheader(2),\
     "./data/mso.csv" using 3:xticlabels(1) with linespoints title columnheader(3)
