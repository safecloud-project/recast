#! /usr/bin/env gnuplot

set terminal pdfcairo enhanced
set output "microbench_encode.pdf"

set title "Encoding latency depending in STeP"
set xlabel "Size of payload (in kB)"
set ylabel "Throughput (in MB/s)"
set xtics 100

set auto x
set style data histogram
set style histogram cluster gap 1
set style fill solid border -1
set boxwidth 0.9 relative
set key inside top center box

set datafile separator ","
plot "./data/encode.csv" using 2:xticlabels(1) title columnhead(2), \
     "./data/encode.csv" using 3:xticlabels(1) title columnhead(3), \
     "./data/encode.csv" using 4:xticlabels(1) title columnhead(4), \
     "./data/encode.csv" using 5:xticlabels(1) title columnhead(5)