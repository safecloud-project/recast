#! /bin/bash
################################################################################
# microbench.sh                                                                #
#                                                                              #
# Gest cProfile from microbenches                                              #
################################################################################

source ./utils.sh

function print_usage {
	echo -e "Usage: ${0} <env-file>\n"
	echo -e "Arguments:"
	echo -e "\tenv-file           Environment file containing the values that should be used by the encoder/decoder"
}

if [[ "${#}" -ne 1 ]]; then
	print_usage
	exit 0
fi

ENV_FILE="${1}"
ENV_FILE_CONTENT="$(cat "${ENV_FILE}")"
source "${ENV_FILE}"
DATA_DIRECTORY="xpdata/cprofile/$(basename "${EC_TYPE}")/"
declare -a SIZES=("4" "16" "64")

cp pycoder/pylonghair_driver.py microbencher/pylonghair_driver.py
cd microbencher
docker build -t pyeclib-microbencher -f pyeclib.Dockerfile .
cd -
mkdir -p "${DATA_DIRECTORY}"


for size in "${SIZES[@]}"; do
	SIZE_IN_BYTES="$((size * 1024 * 1024))"
	docker run -it --rm -v "${PWD}/xpdata/cprofile":/opt/xpdata/cprofile pyeclib-microbencher bash -c "eval ${ENV_FILE_CONTENT} && python -m cProfile -o /opt/xpdata/cprofile/${EC_TYPE}/${size}MB-encode.cProfile /usr/local/src/app/microbench_local_encode.py ${SIZE_IN_BYTES} > /dev/null"
	docker run -it --rm -v "${PWD}/xpdata/cprofile":/opt/xpdata/cprofile pyeclib-microbencher bash -c "eval ${ENV_FILE_CONTENT} && python -m cProfile -o /opt/xpdata/cprofile/${EC_TYPE}/${size}MB-decode.cProfile /usr/local/src/app/microbench_local_decode.py ${SIZE_IN_BYTES} > /dev/null"
	docker run -it --rm -v "${PWD}/xpdata/cprofile":/opt/xpdata/cprofile pyeclib-microbencher bash -c "eval ${ENV_FILE_CONTENT} && python -m cProfile -o /opt/xpdata/cprofile/${EC_TYPE}/${size}MB-reconstruct.cProfile /usr/local/src/app/microbench_local_reconstruct.py ${SIZE_IN_BYTES} > /dev/null"
done
