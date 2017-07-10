# Set terminal
set term pdfcairo enh size 5.00in, 2.00in
set output "cdf.pdf"
set title "1000 PUT requests (4 concurrent) to store 1MB documents"
set key bottom bottom

# Percentage served
set ylabel "percentage served (%)"
set grid y

# Time
set xlabel "time (ms)"
set grid x

# Data
set datafile separator ","
plot "cdf.csv" using 2:1 with lines title "Dagster(5, 2) 3-replication", \
     "cdf.csv" using 3:1 with lines title "Dagster(5, 2)", \
     "cdf.csv" using 4:1 with lines title "STeP(5,2,7) 3-replication", \
     "cdf.csv" using 5:1 with lines title "STeP(5,2,7)"
exit
