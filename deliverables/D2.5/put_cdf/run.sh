#! /usr/bin/env bash

readonly PROGNAME="${0}"

main() {
	
        readonly BASE_DIRECTORY="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
	readonly RUNS=5
	readonly MAIN_HOST="172.16.0.138"
	local directories=(rs)
	for directory in ${directories[@]}; do
		local experiment_directory="${BASE_DIRECTORY}/${directory}"
		scp "${experiment_directory}/docker-compose.yml" "${MAIN_HOST}:playcloud/"
		scp "${experiment_directory}/dispatcher.json" "${MAIN_HOST}:playcloud/pyproxy/"
		for run in $(seq 1 "${RUNS}"); do
			local result_directory="${experiment_directory}/${run}"
			mkdir -p "${result_directory}"
			ssh -o "StrictHostKeyChecking no" "${MAIN_HOST}" "cd playcloud && docker-compose stop && docker-compose rm -fv && sudo find volumes/ -type f -delete && docker-compose build && ./deploy_redis.sh ./ips.txt && docker-compose up -d && sleep 12"
			
			../../../clients/ab_playcloud.sh 500 4 1 172.16.0.138:3000 | tee out.txt
			mv gnuplot-* completion-* out.txt "${result_directory}"
		done
	done
}


main
