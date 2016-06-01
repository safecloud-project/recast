#! /bin/bash
#############################################################################
# A script to load test a playcloud instance.
# The script stores 100 files in the instnance than reads them during
# 1 minute.
# The results are then stored requests.log, total.log
#############################################################################

readonly DIRECTORY="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
readonly DEFAULT_TIMEOUT_IN_SECONDS="60"

#############################################################################
# wait_for_proxy
#
# Wait for the proxy to be able to receive connections by probing its expected
# open port every second for DEFAULT_TIMEOUT_IN_SECONDS seconds.
#############################################################################
function wait_for_proxy {
  local TIMER="${DEFAULT_TIMEOUT_IN_SECONDS}"
  while [[ "${TIMER}" -gt 0 ]]; do
    nc -q 1 "${PROXY_PORT_8080_TCP_ADDR}" "${PROXY_PORT_8080_TCP_PORT}" </dev/null
    if [[ "${?}" -eq 0 ]]; then
      break
    fi
    echo "waiting for proxy ...";
    TIMER=$(( TIMER - 1 ))
    sleep 1
  done

  if [[ "${TIMER}" -eq 0 ]]; then
    echo "Failed to connect to the proxy(${PROXY_PORT_8080_TCP_ADDR}:${PROXY_PORT_8080_TCP_PORT}) after ${DEFAULT_TIMEOUT_IN_SECONDS} seconds"
    exit 1
  fi
}

#############################################################################
# Stores 100 files and prints their name on the screen
#############################################################################
function macrobenchmark_store {
	local size="4"
	local random_file="/tmp/random-${size}.dat"
	dd if=/dev/urandom of="${random_file}"  bs=1048576 count="${size}"
	local ids=""
	local base_url="http://${PROXY_PORT_8080_TCP_ADDR}:${PROXY_PORT_8080_TCP_PORT}"
	for i in $(seq 100); do
		local id="${RANDOM}"
		local target_url="${base_url}/${id}"
		curl --request PUT "${target_url}" --upload-file "${random_file}" --silent
		ids="${ids}\n${target_url}"
	done
	echo -e "${ids}" | tail -n +2
}


#############################################################################
# Load test the system for 1 minute
#############################################################################
function macrobenchmark_test_load {
	local url_file="${1}"
	siege --concurrent=8 --file="${url_file}" --log=/tmp/macrorun/total.log --time=1M --verbose >/tmp/macrorun/requests.log 2>&1
	sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g" -i /tmp/macrorun/requests.log
	chmod -R 0777 /tmp/macrorun/
}

function macrobenchmark_main {
	local url_file="/tmp/macrorun/urls-$(date +%s).txt"
	wait_for_proxy
	macrobenchmark_store > "${url_file}"
	macrobenchmark_test_load "${url_file}"
}

macrobenchmark_main
