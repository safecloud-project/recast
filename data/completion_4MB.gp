# Set terminal
set term png size 1000,1000
set output "completion_4MB.png"
set title "Completion 4 MB"
set key center bottom outside

# Percentage served
set ylabel "Percentage served"
set grid y

# Time
set xlabel "Time in milliseconds"
set grid x

# Data
set datafile separator ","
plot "dummy/completion-1000-50-4.tsv" every ::2 using 2:1 smooth sbezier with lines title "dummy", \
     "jerasure_cauchy/completion-1000-50-4.tsv" every ::2 using 2:1 smooth sbezier with lines title "jerasure_cauchy", \
     "jerasure_vand/completion-1000-50-4.tsv" every ::2 using 2:1 smooth sbezier with lines title "jerasure_vand", \
     "liberasure_vand/completion-1000-50-4.tsv" every ::2 using 2:1 smooth sbezier with lines title "liberasure_vand"
exit
