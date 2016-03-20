#!/bin/bash
../../../papers/DAIS-2016/plots/gen_cdf.rb -c 9 -f ../data/bypass/gnuplot-500-4-4.tsv  					> data/cdf_bypass.txt
../../../papers/DAIS-2016/plots/gen_cdf.rb -c 9 -f ../data/flat_xor_hd_3/gnuplot-500-4-4.tsv  				> data/cdf_flat_xor_hd_3.txt
../../../papers/DAIS-2016/plots/gen_cdf.rb -c 9 -f ../data/flat_xor_hd_4/gnuplot-500-4-4.tsv  				> data/cdf_flat_xor_hd_4.txt
../../../papers/DAIS-2016/plots/gen_cdf.rb -c 9 -f ../data/isa_l_rs_vand/gnuplot-500-4-4.tsv 			    > data/cdf_isa_l_rs_vand.txt
../../../papers/DAIS-2016/plots/gen_cdf.rb -c 9 -f ../data/jerasure_rs_cauchy/gnuplot-500-4-4.tsv 			> data/cdf_jerasure_rs_cauchy.txt
../../../papers/DAIS-2016/plots/gen_cdf.rb -c 9 -f ../data/jerasure_rs_vand/gnuplot-500-4-4.tsv 		    > data/cdf_jerasure_rs_vand.txt
../../../papers/DAIS-2016/plots/gen_cdf.rb -c 9 -f ../data/liberasurecode_rs_vand/gnuplot-500-4-4.tsv  	> data/cdf_liberasurecode_rs_vand.txt
../../../papers/DAIS-2016/plots/gen_cdf.rb -c 9 -f ../data/pylonghair/gnuplot-500-4-4.tsv  				> data/cdf_longhair.txt
../../../papers/DAIS-2016/plots/gen_cdf.rb -c 9 -f ../data/striping/gnuplot-500-4-4.tsv  					> data/cdf_striping.txt

gnuplot macrobench_latency.gp
