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
source "${ENV_FILE}"
FOLDER=${ENV_FILE:4:-4}
DATA_DIRECTORY="results/microbench/encode/${FOLDER}"

echo $DATA_DIRECTORY

declare -a SIZES=("4" "16" "64")

cd pycoder
docker build -t pycoder-micro -f microbencher.Dockerfile .
cd ..
cd microbencher
docker build -t pyeclib-microbencher -f Dockerfile .
cd -
mkdir -p "${DATA_DIRECTORY}"

# Build image
cd pycoder/
docker build -t pycoder-microbench .
cd ../

for size in "${PAYLOAD_SIZES[@]}"; do
	PAYLOAD_SIZE_IN_MB="$((size * 1024 * 1024))"
	for rep in $(seq "${REPETITIONS}"); do
		#docker run -it --rm -v "${PWD}/${DATA_DIRECTORY}":/opt/$DATA_DIRECTORY pyeclib-microbencher \
        #        bash -c "eval ${ENV_FILE_CONTENT} && /usr/local/src/app/microbench_local_encode.py ${ADJUSTED_SIZE} ${REQUESTS} > /opt/$DATA_DIRECTORY/microbench-encode-${size}MB-${rep}.dat"
		docker run --interactive --tty --rm --volume "${PWD}/${DATA_DIRECTORY}":/opt/$DATA_DIRECTORY  ${ENV_VARIABLES} --entrypoint /usr/local/src/app/microbench_local_encode.py pycoder-microbench "${PAYLOAD_SIZE_IN_MB} ${REQUESTS}" > $DATA_DIRECTORY/microbench-encode-${size}MB-${rep}.dat
	done
done
