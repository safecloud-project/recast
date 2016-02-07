#! /bin/bash
###############################################################################
# microbench.sh                                                               #
#                                                                             #
# Benchmarks a GRPC enabled encoder/decoder implementing the behaviour        #
# defined in playclcoud.proto.                                                #
###############################################################################

source ./utils.sh

function print_usage {
	echo -e "Usage: ${0} <coder-host> <archive> <env-file> <repetitions>\n"
	echo -e "Arguments:"
	echo -e "\tcoder-host         IP address fo the machine hosting the encoder/decoder"
	echo -e "\tarchive            Archive containing the repo's code"
	echo -e "\tenv-file           Environment file containing the values that should be used by the encoder/decoder"
	echo -e "\trepetitions        Number of repetitions"
}

if [[ "${#}" -ne 4 ]]; then
	print_usage
	exit 0
fi

CODER_HOST="${1}"
ARCHIVE="${2}"
ENV_FILE="${3}"
REPETITIONS="${4}"
DATA_DIRECTORY="xpdata/$(basename "${ENV_FILE}")/"
declare -a SIZES=("4" "16" "64")

cd microbencher/
docker build -t microbencher .
cd -
mkdir -p "${DATA_DIRECTORY}"

for size in "${SIZES[@]}"; do
	ADJUSTED_SIZE="$((size * 1024 * 1024))"
	for rep in $(seq "${REPETITIONS}"); do
		source exports.source
		setup_coder "${CODER_HOST}" "${ARCHIVE}" "${ENV_FILE}"
		docker run -it --rm -v "${PWD}/xpdata":/opt/xpdata microbencher /bin/bash -c "java -jar target/microbencher-1.0-SNAPSHOT-jar-with-dependencies.jar --host ${DUMMY_CODER_PORT_1234_TCP_ADDR} --port ${DUMMY_CODER_PORT_1234_TCP_PORT} --size ${ADJUSTED_SIZE} > /opt/$DATA_DIRECTORY/microbench-${size}MB-${rep}.dat"
	done
done
