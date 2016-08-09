#! /bin/bash
################################################################################
# macrobenchmark.sh
#
# Run a macrobenchmark of the playcloud setup
################################################################################

source ./utils.sh

function print_usage {
  echo -e "Usage: ${0} <proxy-ip> <coder-ip> <archive> payload-size [payload-size [payload-size [...]]]"
  echo -e ""
  echo -e "Benchmark an encoder/decoder."
  echo -e ""
  echo -e "Arguments:"
  echo -e "\tproxy-ip     IP address of the machine that will host the proxy instance"
  echo -e "\tcoder-ip     IP address of the machine that will host the encoder/decoder instance"
  echo -e "\tarchive      The archive containing the repo's code"
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

function macrobench_config {
  local conf_file="${1}"
  local block_sizes="${2}"
  local env_file="$(transform_to_bash_env_file "${conf_file}")"
  source "${env_file}"
  for block_size in ${block_sizes} ; do
    setup_proxy "${PROXY_HOST}" "${ARCHIVE}" "${env_file}"
    setup_coder "${CODER_HOST}" "${ARCHIVE}" "${env_file}"
    for redis_hostname in $(clients/list_redis_hostnames.py); do
      setup_redis "${redis_hostname}" "${ARCHIVE}" "${env_file}"
    done
    source exports.source
    directory_name="$(dirname ${conf_file} | sed 's/dockerenv\///')/$(basename ${conf_file} | sed 's/.cfg//')"
    mkdir -p "${PWD}/xpdata/macrobench/${directory_name}"
    # Wait for connection to proxy server to be available
    wait_for_proxy
    # Take storage provider memory usage at the start
    pyproxy/get_quota.py > "${PWD}/xpdata/macrobench/${directory_name}/quota_start_${block_size}.json"
    docker run -it --rm -v "${PWD}/xpdata":/opt/xpdata client /bin/bash -c "cd /opt/xpdata/macrobench/${directory_name} && /ab_playcloud.sh 250 ${CONCURRENT_REQUESTS} ${block_size} ${PROXY_PORT_3000_TCP_ADDR}:${PROXY_PORT_3000_TCP_PORT} > stdout-${block_size}.txt 2>&1"
    # Take redis memory footprint
    clients/get_redis_info.py > "${PWD}/xpdata/macrobench/${directory_name}/info_all_${block_size}.json"
    # Take storage provider memory usage at the end
    pyproxy/get_quota.py > "${PWD}/xpdata/macrobench/${directory_name}/quota_end_${block_size}.json"
    # Clear storage provider of data
    clients/flush_redis_instances.py
    # pyproxy/flush_providers
  done
}

if [[ "${#}" -lt 4 ]]; then
  print_usage
  exit 0
fi

readonly PROXY_HOST="${1}"
shift
readonly CODER_HOST="${1}"
shift
readonly ARCHIVE="${1}"
shift

# Set the number of concurrent requests sent by ab_playcloud to # of cores * 2
readonly CONCURRENT_REQUESTS="$(( $(grep -c ^processor /proc/cpuinfo) * 2 ))"

cd clients
docker build -t client .
cd -
mkdir -p xpdata/
readonly BLOCK_SIZES=$@
for conf_file in $(find dockerenv/ -maxdepth 2 -type f); do
  macrobench_config "${conf_file}" "${BLOCK_SIZES}"
done
