set term postscript monochrome eps enhanced 22
set output "macrobench_latency.eps"
load "../../../papers/DAIS-2016/plots/styles.inc"

X_MARGIN=0.14
Y_MARGIN=0.04
WIDTH_IND=0.26
HEIGHT_IND=0.31
WIDTH_BETWEEN_X=0.02
WIDTH_BETWEEN_Y=-0.035

set size 1,0.9
# do not change the plot width. This is what keeps the font size the same
# in all the paper and plots.

set bmargin 1
set tmargin 1
set lmargin 1
set rmargin 0

set multiplot
unset key

X_POS=0
Y_POS=0
set origin X_MARGIN+(X_POS*(WIDTH_IND+WIDTH_BETWEEN_X)), Y_MARGIN+(Y_POS*(HEIGHT_IND+WIDTH_BETWEEN_Y))
set size WIDTH_IND,HEIGHT_IND

set title "isa\\_l\\_rs\\_vand" offset 0,-0.5 font "Arial,16pt" 
#set xlabel "millisecond"
set ylabel "CDF (%)"
set xrange [0:3000]
set xtics ("0" 0, "1s" 1000, "2s" 2000, "3s" 3000, "4s" 4000)
set yrange [0:100]
set grid x,y
set ytics 0,20,100
set key bottom right samplen 1 width 1
set nokey
plot \
	'data/cdf_isa_l_rs_vand.txt'	u ($1):($6*100) w l ls 4 notitle '',\
	'data/cdf_isa_l_rs_vand.txt'	u ($1):($6*100) every 50 w p ls 1 notitle ''

X_POS=1
Y_POS=0
set origin X_MARGIN+(X_POS*(WIDTH_IND+WIDTH_BETWEEN_X)), Y_MARGIN+(Y_POS*(HEIGHT_IND+WIDTH_BETWEEN_Y))
set size WIDTH_IND,HEIGHT_IND

set title "jerasure\\_rs\\_cauchy" offset 0,-0.5
#set xlabel "millisecond"
set ylabel "CDF (%)"
unset ylabel
set xrange [0:]
#set xtics ("0" 0,"5s" 5000,"10s" 10000,"15s" 15000,"20s" 20000,"25s" 25000)
set yrange [0:100]
set grid x,y
set ytics (" " 0," " 20," " 40," " 60," " 80," " 100)
#set ytics 0,20,100
set key bottom right samplen 1 width 1

plot \
	'data/cdf_jerasure_rs_cauchy.txt' u ($1):($6*100) w l ls 4 notitle 'jerasure\_rs\_cauchy',\
	'data/cdf_jerasure_rs_cauchy.txt' u ($1):($6*100) every 50 w p ls 1 notitle ''


X_POS=2
Y_POS=0
set origin X_MARGIN+(X_POS*(WIDTH_IND+WIDTH_BETWEEN_X)), Y_MARGIN+(Y_POS*(HEIGHT_IND+WIDTH_BETWEEN_Y))
set size WIDTH_IND,HEIGHT_IND

set title "jerasure\\_rs\\_vand" offset 0,-0.5
#set xlabel "millisecond"
set ylabel "CDF (%)"
unset ylabel
set xrange [0:]
#set xtics ("0" 0,"5s" 5000,"10s" 10000,"15s" 15000,"20s" 20000,"25s" 25000)
set yrange [0:100]
set grid y
set ytics (" " 0," " 20," " 40," " 60," " 80," " 100)
set key bottom right samplen 1 width 1

plot \
	'data/cdf_jerasure_rs_vand.txt'  u ($1):($6*100) w l ls 4 notitle 'jerasure\_rs\_vand',\
	'data/cdf_jerasure_rs_vand.txt'  u ($1):($6*100) every 50 w p ls 1 notitle ''


X_POS=0
Y_POS=1
set origin X_MARGIN+(X_POS*(WIDTH_IND+WIDTH_BETWEEN_X)), Y_MARGIN+(Y_POS*(HEIGHT_IND+WIDTH_BETWEEN_Y))
set size WIDTH_IND,HEIGHT_IND

set title "liberasure\\_flat\\_xor\\_3" offset 0,-0.7
#set xlabel "millisecond"
set ylabel "CDF (%)"
#unset ylabel
set xrange [0:]
set xtics ("" 0, "" 1000, "" 2000, "" 3000, "" 4000)
#set xtics ("0" 0,"5s" 5000,"10s" 10000,"15s" 15000,"20s" 20000,"25s" 25000)
set yrange [0:100]
set grid y
set ytics 0,20,100
#set ytics (" " 0," " 20," " 40," " 60," " 80," " 100)
set key bottom right samplen 1 width 1

plot \
	'data/cdf_flat_xor_hd_3.txt'  u ($1):($6*100) w l ls 4 notitle '',\
	'data/cdf_flat_xor_hd_3.txt'  u ($1):($6*100) every 50 w p ls 1 notitle ''



X_POS=1
Y_POS=1
set origin X_MARGIN+(X_POS*(WIDTH_IND+WIDTH_BETWEEN_X)), Y_MARGIN+(Y_POS*(HEIGHT_IND+WIDTH_BETWEEN_Y))
set size WIDTH_IND,HEIGHT_IND

set title "liberasure\\_flat\\_xor\\_4" offset 0,-0.7 font "Arial,16pt"
#set xlabel "millisecond"
unset ylabel 
set xrange [0:]
set grid x,y
#set xtics ("0" 0,"5s" 5000,"15s" 15000)
set yrange [0:100]
set grid y
set ytics (" " 0," " 20," " 40," " 60," " 80," " 100)
#set ytics 0,20,100
set key bottom right samplen 1 width 1
set nokey
plot \
	'data/cdf_flat_xor_hd_4.txt'	u ($1):($6*100) w l ls 4 notitle '',\
	'data/cdf_flat_xor_hd_4.txt'	u ($1):($6*100) every 50 w p ls 1 notitle ''
 			                  

X_POS=2
Y_POS=1
set origin X_MARGIN+(X_POS*(WIDTH_IND+WIDTH_BETWEEN_X)), Y_MARGIN+(Y_POS*(HEIGHT_IND+WIDTH_BETWEEN_Y))
set size WIDTH_IND,HEIGHT_IND

set title "liberasure\\_rs\\_vand" offset 0,-0.7 
#set xlabel "millisecond"
set ylabel "CDF (%)"
unset ylabel
set xrange [0:]
#set xtics ("0" 0,"5s" 5000,"10s" 10000,"15s" 15000,"20s" 20000,"25s" 25000)
set yrange [0:100]
set grid y
set ytics (" " 0," " 20," " 40," " 60," " 80," " 100)
#set ytics 0,20,100
set key bottom right samplen 1 width 1

plot \
	'data/cdf_liberasurecode_rs_vand.txt' u ($1):($6*100) w l ls 4 notitle '',\
	'data/cdf_liberasurecode_rs_vand.txt' u ($1):($6*100) every 50 w p ls 1 notitle '',\
	 

X_POS=0
Y_POS=2
set origin X_MARGIN+(X_POS*(WIDTH_IND+WIDTH_BETWEEN_X)), Y_MARGIN+(Y_POS*(HEIGHT_IND+WIDTH_BETWEEN_Y))
set size WIDTH_IND,HEIGHT_IND

set title "longhair\\_cauchy\\_256" offset 0,-0.7
#set xlabel "millisecond"
set ylabel "CDF (%)"
#unset ylabel
set xrange [0:]

#set xtics ("0" 0,"5s" 5000,"10s" 10000,"15s" 15000,"20s" 20000,"25s" 25000)
set yrange [0:100]
set ytics 0,20,100

set grid y
#set ytics (" " 0," " 20," " 40," " 60," " 80," " 100)
set key bottom right samplen 1 width 1

plot \
	'data/cdf_longhair.txt'  u ($1):($6*100) w l ls 4 notitle '',\
	'data/cdf_longhair.txt'  u ($1):($6*100) every 50 w p ls 1 notitle '' 


X_POS=1
Y_POS=2
set origin X_MARGIN+(X_POS*(WIDTH_IND+WIDTH_BETWEEN_X)), Y_MARGIN+(Y_POS*(HEIGHT_IND+WIDTH_BETWEEN_Y))
set size WIDTH_IND,HEIGHT_IND

set title "striping" offset 0,-0.7
#set xlabel "millisecond"
set ylabel "CDF (%)"
unset ylabel
set xrange [0:]
#set xtics ("0" 0,"5s" 5000,"10s" 10000,"15s" 15000,"20s" 20000,"25s" 25000)
set yrange [0:100]
set grid y
set ytics (" " 0," " 20," " 40," " 60," " 80," " 100)
set key bottom right samplen 1 width 1

plot \
	'data/cdf_striping.txt'  u ($1):($6*100) w l ls 4 notitle '',\
	'data/cdf_striping.txt'  u ($1):($6*100) every 50 w p ls 1 notitle '' 
					  						  

X_POS=2
Y_POS=2
set origin X_MARGIN+(X_POS*(WIDTH_IND+WIDTH_BETWEEN_X)), Y_MARGIN+(Y_POS*(HEIGHT_IND+WIDTH_BETWEEN_Y))
set size WIDTH_IND,HEIGHT_IND

set title "bypass" offset 0,-0.7
#set xlabel "millisecond"
unset ylabel
set xrange [0:]
#set xtics ("0" 0,"5s" 5000,"10s" 10000,"15s" 15000,"20s" 20000,"25s" 25000)
set yrange [0:100]
set grid y
set ytics (" " 0," " 20," " 40," " 60," " 80," " 100)
set key bottom right samplen 1 width 1

plot \
	'data/cdf_bypass.txt' u ($1):($6*100) w l ls 4 notitle '',\
	'data/cdf_bypass.txt' u ($1):($6*100) every 20 w p ls 1 notitle ''
				  						 
							  
!epstopdf "macrobench_latency.eps"
!rm "macrobench_latency.eps"
quit
