#! /usr/bin/env gnuplot
# Set terminal
set term pdfcairo enh size 5.00in, 2.00in
set output "cdf.pdf"
set title "500 PUT requests (4 concurrent) to store 1MB documents"
set key bottom
set pointsize 0.5

# Percentage served
set ylabel "percentage served (%)"
set grid y

# Time
set xlabel "time (ms)"
set grid x

# Data
set datafile separator ","
plot "cdf.csv" using 4:1 with lines linetype 1 linecolor 1 title "RS(10, 4)", \
     "cdf.csv" using 4:1 every 10 with points pointtype 12 linecolor 1 notitle, \
     "cdf.csv" using 2:1 with lines linecolor 2 title "Dagster(1, 10) 3-replication", \
     "cdf.csv" using 2:1 every 10 with points pointtype 13 linecolor 2 notitle, \
     "cdf.csv" using 3:1 with lines linecolor 3 title "Dagster(1, 10)", \
     "cdf.csv" using 3:1 every 10 with points pointtype 13 linecolor 3 notitle, \
     "cdf.csv" using 5:1 with lines linecolor 4 title "STeP(1, 10, 3) 3-replication", \
     "cdf.csv" using 5:1 every 10 with points pointtype 26 linecolor 4 notitle, \
     "cdf.csv" using 6:1 with lines linecolor 5 title "STeP(1, 10, 3)", \
     "cdf.csv" using 6:1 every 10 with points pointtype 26 linecolor 5 notitle
exit
