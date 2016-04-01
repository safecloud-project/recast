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
}

if [[ "${#}" -ne 2 ]]; then
	print_usage
	exit 0
fi

ENV_FILE="${1}"
ENV_VARIABLES="$(cat ${ENV_FILE}  | sed -e s/export/-e/ | sed -e ':a;N;$!ba;s/\n/ /g')"
REPETITIONS="${2}"
DATA_DIRECTORY="xpdata/pyeclib/$(basename "${EC_TYPE}")/"
declare -a PAYLOAD_SIZES=("4" "16" "64")

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
		docker run --interactive --tty --rm --volume "${PWD}/xpdata/pyeclib":/opt/xpdata/pyeclib  ${ENV_VARIABLES} --entrypoint /usr/local/src/app/microbench_local_encode.py pycoder-microbench "${PAYLOAD_SIZE_IN_MB}" > $DATA_DIRECTORY/microbench-encode-${size}MB-${rep}.dat
	done
done
