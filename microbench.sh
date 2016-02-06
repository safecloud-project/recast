#! /bin/bash

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

cd microbencher/
docker build -t microbencher .
cd -
mkdir -p xpdata

for rep in $(seq ${REPETITIONS}); do
	source exports.source
	setup_coder "${CODER_HOST}" "${ARCHIVE}" "${ENV_FILE}"
	docker run -it --rm -v "${PWD}/xpdata":/opt/xpdata microbencher /bin/bash -c "java -jar target/microbencher-1.0-SNAPSHOT-jar-with-dependencies.jar --host ${DUMMY_CODER_PORT_1234_TCP_ADDR} --port ${DUMMY_CODER_PORT_1234_TCP_PORT} > /opt/xpdata/microbench-${rep}.dat"
done
