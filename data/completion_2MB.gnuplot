# output as png image
set terminal jpeg

# save file to "out.png"
set output "completion_2MB.jpeg"

# graph title
set title "completion 2 MB"

# nicer aspect ratio for image size
set size 1,0.7

# y-axis grid
set grid y

# x-axis label
set xlabel "time (ms)"

# y-axis label
set ylabel "completion (%)"

# column separator
set datafile separator ','

plot "data/dummy/completion-1000-50-2.tsv" using 2:1 smooth sbezier with lines title "dummy", \
     "data/jerasure_cauchy/completion-1000-50-2.tsv" using 2:1 smooth sbezier with lines title "jerasure_cauchy", \
     "data/jerasure_vand/completion-1000-50-2.tsv" using 2:1 smooth sbezier with lines title "jerasure_vand", \
     "data/liberasure_vand/completion-1000-50-2.tsv" using 2:1 smooth sbezier with lines title "liberasure_vand"
