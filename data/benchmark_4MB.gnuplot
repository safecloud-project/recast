# Let's output to a jpeg file
set terminal jpeg size 500,500

# This sets the aspect ratio of the graph
set size 1, 1

# The file we'll write to
set output "4MB.jpeg"

# The graph title
set title "1000 requests (50 concurrent) with 4 MB payload RS(10, 4)"

# Where to place the legend/key
set key left top

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

# Tell gnuplot to use tabs as the delimiter instead of spaces (default)
set datafile separator '\t'

# Plot the data
plot "data/dummy/corrected_gnuplot-1000-50-2.tsv" every ::2 using 2:5 title "dummy" with points, \
     "data/jerasure_cauchy/corrected_gnuplot-1000-50-4.tsv" every ::2 using 2:5 title "jerasure_cauchy" with points, \
     "data/jerasure_vand/corrected_gnuplot-1000-50-4.tsv" every ::2 using 2:5 title "jerasure_vand" with points, \
     "data/liberasure_vand/corrected_gnuplot-1000-50-4.tsv" every ::2 using 2:5 title "liberasure_vand" with points

exit
