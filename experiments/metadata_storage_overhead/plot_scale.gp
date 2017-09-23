#! /usr/bin/env gnuplot
set terminal pdfcairo enhanced
set output "mso_scale .pdf"

set title "Metadata size over time"
set xlabel "Number of documents"
set ylabel "Size (in bytes)"
set xtics 100

set grid ytics

set key inside top left box

set logscale y

set datafile separator ","
plot "./data/mso.csv" using 2:xticlabels(1) with lines title columnhead(2), \
     "./data/mso.csv" using 3:xticlabels(1) with lines title columnhead(3), \
     "./data/mso.csv" using 4:xticlabels(1) with lines title columnhead(4), \
     "./data/mso.csv" using 5:xticlabels(1) with lines title columnhead(5)
