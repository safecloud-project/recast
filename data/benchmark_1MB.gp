# Let's output to a pdf file
set term pdfcairo enh size 5in,5in

# This sets the aspect ratio of the graph
set size 1, 1

# The file we'll write to
set output "1MB.pdf"

# The graph title
set title "1000 requests (50 concurrent) with 1 MB payload RS(10, 4)"

# Draw gridlines oriented on the y axis
set grid y

# Specify that the x-series data is time data
set xdata time

# Specify the *input* format of the time data
set timefmt "%s"

# Specify the *output* format for the x-axis tick labels
set format x "%S"

# Label the x-axis
set xlabel 'seconds'

# Label the y-axis
set ylabel "response time (ms)"

set key center bottom outside

# Tell gnuplot to use tabs as the delimiter instead of spaces (default)
set datafile separator '\t'

# Plot the data
plot \
     "bypass/corrected_gnuplot-1000-50-1.tsv" every ::2 using 2:5 title "bypass" with points, \
     "dummy/corrected_gnuplot-1000-50-1.tsv" every ::2 using 2:5 title "dummy" with points, \
     "jerasure_cauchy/corrected_gnuplot-1000-50-1.tsv" every ::2 using 2:5 title "jerasure\\_cauchy" with points, \
     "jerasure_vand/corrected_gnuplot-1000-50-1.tsv" every ::2 using 2:5 title "jerasure\\_vand" with points, \
     "liberasure_vand/corrected_gnuplot-1000-50-1.tsv" every ::2 using 2:5 title "liberasure\\_vand" with points
exit
