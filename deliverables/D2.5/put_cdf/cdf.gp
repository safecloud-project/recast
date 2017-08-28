#! /usr/bin/env gnuplot
# Set terminal
set term pdfcairo enh size 5.00in, 2.00in
set output "cdf.pdf"
set title "500 PUT requests (4 concurrent) to store 1MB documents"
set key bottom

# Percentage served (y-axis)
set ylabel "percentage served (%)"
set grid y

# Time (x-axis)
set xlabel "time (ms)"
set grid x

# Plot lines style
set pointsize 0.5
set pointinterval 10 # Draw every 10 points
set style line 1 linetype 1 pointtype 13 pointinterval 10 linecolor rgb "#DC143C"# Dagster with replication
set style line 2 linetype 2 pointtype 13 pointinterval 10 linecolor rgb "#E9967A" # Dagster
set style line 3 linetype 3 pointtype 26 pointinterval 10 linecolor rgb "#00008B" # STeP with replication
set style line 4 linetype 4 pointtype 26 pointinterval 10 linecolor rgb "#00BFFF" # STeP

# Data
set datafile separator ","
plot "cdf.csv" using 3:1 with linespoints linestyle 2 title "Dagster(1, 10)", \
     "cdf.csv" using 2:1 with linespoints linestyle 1 title "Dagster(1, 10) 3-replication", \
     "cdf.csv" using 6:1 with linespoints linestyle 4 title "STeP(1, 10, 3)", \
     "cdf.csv" using 5:1 with linespoints linestyle 3 title "STeP(1, 10, 3) 3-replication"
exit
