# Set terminal
set term pdfcairo enh size 5.00in, 2.00in
set output "completion_1MB.pdf"
set title "1000 requests (50 concurrent) with 1 MB payload RS(10, 4)"
set key bottom right box

# Percentage served
set ylabel "percentage served (%)"
set grid y

# Time
set xlabel "time (ms)"
set grid x

# Data
set datafile separator ","
plot \
     "bypass/completion-1000-50-1.csv" every ::2 using 2:1 smooth sbezier with lines title "bypass", \
     "dummy/completion-1000-50-1.csv" every ::2 using 2:1 smooth sbezier with lines title "dummy", \
     "jerasure_cauchy/completion-1000-50-1.tsv" every ::2 using 2:1 smooth sbezier with lines title "jerasure\\_cauchy", \
     "jerasure_vand/completion-1000-50-1.tsv" every ::2 using 2:1 smooth sbezier with lines title "jerasure\\_vand", \
     "liberasure_vand/completion-1000-50-1.tsv" every ::2 using 2:1 smooth sbezier with lines title "liberasure\\_vand"
exit
