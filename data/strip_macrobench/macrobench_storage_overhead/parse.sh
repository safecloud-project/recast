#!/bin/bash
rm data/overhead_final.txt
touch data/overhead_final.txt

baseline=2097186065

echo -n "bypass " >> data/overhead_final.txt
grep "total_net_input_bytes" ../data/bypass/info_all.txt  				| cut -f 2 -d ":"  >> data/overhead_final.txt

echo -n "striping " >> data/overhead_final.txt
grep "total_net_input_bytes" ../data/striping/info_all.txt  			| cut -f 2 -d ":"  >> data/overhead_final.txt

echo -n "\"flat\\\_xor\\\_hd\\\_3\" " >> data/overhead_final.txt
grep "total_net_input_bytes" ../data/flat_xor_hd_3/info_all.txt  		| cut -f 2 -d ":"  >> data/overhead_final.txt

echo -n "\"flat\\\_xor\\\_hd\\\_4\" " >> data/overhead_final.txt
grep "total_net_input_bytes" ../data/flat_xor_hd_4/info_all.txt  		| cut -f 2 -d ":"  >> data/overhead_final.txt

echo -n "isa\\\_l\\\_rs\\\_vand " >> data/overhead_final.txt
grep "total_net_input_bytes" ../data/isa_l_rs_vand/info_all.txt 		| cut -f 2 -d ":"  >> data/overhead_final.txt

echo -n "jerasure\\\_rs\\\_cauchy " >> data/overhead_final.txt
grep "total_net_input_bytes" ../data/jerasure_rs_cauchy/info_all.txt 	| cut -f 2 -d ":"  >> data/overhead_final.txt

echo -n "jerasure\\\_rs\\\_vand " >> data/overhead_final.txt
grep "total_net_input_bytes" ../data/jerasure_rs_vand/info_all.txt 		| cut -f 2 -d ":"  >> data/overhead_final.txt

echo -n "liberasurecode\\\_rs\\\_vand " >> data/overhead_final.txt
grep "total_net_input_bytes" ../data/liberasurecode_rs_vand/info_all.txt| cut -f 2 -d ":"  >> data/overhead_final.txt

echo -n "pylonghair " >> data/overhead_final.txt
grep "total_net_input_bytes" ../data/pylonghair/info_all.txt  			| cut -f 2 -d ":"  >> data/overhead_final.txt

gnuplot macrobench_storage_overhead.gp
