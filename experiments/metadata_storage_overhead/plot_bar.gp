#! /usr/bin/env gnuplot
set terminal pdfcairo enhanced
set output "mso_bar.pdf"

set title "Metadata size over time"
set xlabel "Number of documents"
set ylabel "Size (in bytes)"

set auto x
set style data histogram
set style histogram cluster gap 1
set style fill solid border -1
set boxwidth 0.9 relative
set key inside top left box

set datafile separator ","
plot "./data/mso.csv" using 2:xticlabels(1) title columnhead(2), \
     "./data/mso.csv" using 3:xticlabels(1) title columnhead(3), \
     "./data/mso.csv" using 4:xticlabels(1) title columnhead(4), \
     "./data/mso.csv" using 5:xticlabels(1) title columnhead(5)
