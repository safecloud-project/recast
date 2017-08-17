#! /usr/bin/env gnuplot
set term pdfcairo enh
set output "storage_overhead.pdf"

set title "STeP(1, 10, 3) Storage overhead when scrubbing\n replicas of blocks pointed 3 or more times"
set xlabel "# of documents"
set ylabel "# of replicas\n == \n# of blocks * replication factor"

set style data lines

set xrange [1:20]

set datafile separator ","
plot (x * 9)                  with filledcurves below x1 linetype rgb "#FF4500" title "blocks initially stored", \
     "./data/scrub.csv" using 1:2 with filledcurves below x1 linetype rgb "#228B22" title "blocks actually  stored"
 
exit
