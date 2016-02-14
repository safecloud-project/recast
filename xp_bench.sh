#! /bin/bash

source ./utils.sh

function print_usage {
  echo -e "Usage: ${0} <proxy-ip> <coder-ip> <redis-ip> <archive> <env-file> payload-size [payload-size [payload-size [...]]]"
  echo -e ""
  echo -e "Benchmark an encoder/decoder."
  echo -e ""
  echo -e "Arguments:"
	echo -e "\tproxy-ip     IP address of the machine that will host the proxy instance"
	echo -e "\tcoder-ip     IP address of the machine that will host the encoder/decoder instance"
	echo -e "\tredis-ip     IP address of the machine that will host the redis instance"
  echo -e "\tarchive      The archive containing the repo's code"
	echo -e "\tenv-file     A file containing configuration values that the application should be using"
  echo -e ""
}

if [[ "${#}" -lt 6 ]]; then
  print_usage
  exit 0
fi

readonly PROXY_HOST="${1}"
shift
readonly CODER_HOST="${1}"
shift
readonly REDIS_HOST="${1}"
shift
readonly ARCHIVE="${1}"
shift
readonly ENV_FILE="${1}"
shift

# Set the number of concurrent requests sent by ab_playcloud to # of cores * 2
readonly CONCURRENT_REQUESTS="$(( $(grep -c ^processor /proc/cpuinfo) * 2 ))"

cd client_bash/
docker build -t client .
cd -
mkdir -p xpdata/
source "${ENV_FILE}"
for i in $(seq 10); do
  for BLOCK_SIZE in "$@"; do
    setup_proxy "${PROXY_HOST}" "${ARCHIVE}" "${ENV_FILE}"
    setup_coder "${CODER_HOST}" "${ARCHIVE}" "${ENV_FILE}"
    setup_redis "${REDIS_HOST}" "${ARCHIVE}" "${ENV_FILE}"
    source exports.source
    mkdir -p "${PWD}/xpdata/macrobench/${EC_TYPE}/${i}"
    docker run -it --rm -v "${PWD}/xpdata":/opt/xpdata client /bin/bash -c "cd /opt/xpdata/macrobench/${EC_TYPE}/${i} && ls /home && /ab_playcloud.sh 1000 ${CONCURRENT_REQUESTS} ${BLOCK_SIZE} ${PROXY_PORT_3000_TCP_ADDR}:${PROXY_PORT_3000_TCP_PORT} > stdout.txt"
  done
done
