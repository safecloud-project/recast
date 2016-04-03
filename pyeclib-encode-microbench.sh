#! /bin/bash
###############################################################################
# microbench.sh                                                               #
#                                                                             #
# Benchmarks a GRPC enabled encoder/decoder implementing the behaviour        #
# defined in playclcoud.proto.                                                #
###############################################################################

source ./utils.sh

function print_usage {
	echo -e "Usage: ${0} <env-file> <repetitions>\n"
	echo -e "Arguments:"
	echo -e "\tenv-file           Environment file containing the values that should be used by the encoder/decoder"
	echo -e "\trepetitions        Number of repetitions"
	echo -e "\trequests           Number of requests"
}

if [[ "${#}" -ne 3 ]]; then
	print_usage
	exit 0
fi

ENV_FILE="${1}"
ENV_VARIABLES="$(cat ${ENV_FILE}  | sed -e s/export/-e/ | sed -e ':a;N;$!ba;s/\n/ /g')"
REPETITIONS="${2}"
REQUESTS=${3}
#source "${ENV_FILE}"
FOLDER=${ENV_FILE:10:-4}
DATA_DIRECTORY="results/microbench/encode/${FOLDER}"

echo $DATA_DIRECTORY

declare -a PAYLOAD_SIZES=("4" "16" "64")


mkdir -p "${DATA_DIRECTORY}"

cd pycoder/
docker build -t pycoder-micro -f microbencher.Dockerfile .
cd ..
mkdir -p ${DATA_DIRECTORY}


for size in "${PAYLOAD_SIZES[@]}"; do
	PAYLOAD_SIZE_IN_MB="$((size * 1024 * 1024))"
	for rep in $(seq "${REPETITIONS}"); do
		cd microbencher

		cp EncodeDockerfileTemplate Dockerfile

		#Add aparemter to the docker file
		sed -i "s|{DATA_DIR}|${DATA_DIRECTORY}|g" Dockerfile
		sed -i "s/{PAYLOAD}/${PAYLOAD_SIZE_IN_MB}/g" Dockerfile
		sed -i "s/{REQ}/${REQUESTS}/g" Dockerfile
		sed -i "s/{SIZE}/${size}/g" Dockerfile
		sed -i "s/{REP}/${rep}/g" Dockerfile

		#Add enviroment variables to the docker file
		sed -i "/{ENV}/r ../${ENV_FILE}" Dockerfile
		sed -i "/{ENV}/d" Dockerfile
		
		docker build -t pycoder-microbencher -f Dockerfile .
		cd ..
		dstat -t -c -d -m -n > ${DATA_DIRECTORY}/microbench-encode-${size}MB-${rep}.csv  &
		docker run --rm --volume "${PWD}/${DATA_DIRECTORY}":/$DATA_DIRECTORY pycoder-microbencher
		kill -9 $!
	done
done
