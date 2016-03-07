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

readonly DEFAULT_TIMEOUT_IN_SECONDS=60

################################################################################
# wait_for_proxy
#
# Wait for the proxy to be able to receive connections by probing its expected
# open port every second for DEFAULT_TIMEOUT_IN_SECONDS seconds.
################################################################################
function wait_for_proxy {
  local TIMER="${DEFAULT_TIMEOUT_IN_SECONDS}"
  while [[ "${TIMER}" -gt 0 ]]; do
    nc -q 1 "${PROXY_PORT_3000_TCP_ADDR}" "${PROXY_PORT_3000_TCP_PORT}" </dev/null
    if [[ "${?}" -eq 0 ]]; then
      break
    fi
    echo "waiting for proxy ...";
    TIMER=$(( TIMER - 1 ))
    sleep 1
  done

  if [[ "${TIMER}" -eq 0 ]]; then
    echo "Failed to connect to the proxy(${PROXY_PORT_3000_TCP_ADDR}:${PROXY_PORT_3000_TCP_PORT}) after ${DEFAULT_TIMEOUT_IN_SECONDS} seconds"
    exit 1
  fi
}

################################################################################
# wait_for_redis
#
# Wait for the redis database to be able to receive connections
################################################################################
function wait_for_redis {
  local TIMER="${DEFAULT_TIMEOUT_IN_SECONDS}"
  while [[ "${TIMER}" -gt 0 ]]; do
    nc -q 1 "${REDIS_PORT_6379_TCP_ADDR}" "${REDIS_PORT_6379_TCP_PORT}" </dev/null
    if [[ "${?}" -eq 0 ]]; then
      break
    fi
    echo "waiting for redis ...";
    TIMER=$(( TIMER - 1 ))
    sleep 1
  done

  if [[ "${TIMER}" -eq 0 ]]; then
    echo "Failed to connect to redis (${REDIS_PORT_6379_TCP_ADDR}:${REDIS_PORT_6379_TCP_PORT}) after ${DEFAULT_TIMEOUT_IN_SECONDS} seconds"
    exit 1
  fi
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

cd clients
docker build -t client .
cd -
mkdir -p xpdata/
source "${ENV_FILE}"
for BLOCK_SIZE in "$@"; do
  setup_proxy "${PROXY_HOST}" "${ARCHIVE}" "${ENV_FILE}"
  setup_coder "${CODER_HOST}" "${ARCHIVE}" "${ENV_FILE}"
  setup_redis "${REDIS_HOST}" "${ARCHIVE}" "${ENV_FILE}"
  source exports.source
  mkdir -p "${PWD}/xpdata/macrobench/${EC_TYPE}"
  # Wait for connection to proxy server to be available
  wait_for_proxy
  wait_for_redis
  docker run -it --rm -v "${PWD}/xpdata":/opt/xpdata client /bin/bash -c "cd /opt/xpdata/macrobench/${EC_TYPE} && /ab_playcloud.sh 500 ${CONCURRENT_REQUESTS} ${BLOCK_SIZE} ${PROXY_PORT_3000_TCP_ADDR}:${PROXY_PORT_3000_TCP_PORT} > stdout.txt 2>&1"
  # Take memory footprint
  redis-cli -h "${REDIS_PORT_6379_TCP_ADDR}" -p "${REDIS_PORT_6379_TCP_PORT}" INFO all > "${PWD}/xpdata/macrobench/${EC_TYPE}/info_all.txt"
done
