#! /usr/bin/env bash

readonly DEFAULT_TIMEOUT_IN_SECONDS=60
#############################################################################
# Check if all the variables needed to run the benchmark are defined
#############################################################################
function ycsb_check_variables {
	if [[ -z "${YCSB_HOME}" ]]; then
		echo "YCSB_HOME env variable must be defined" >&2
		exit 1
	fi

	if [[ -z "${WORKLOAD}" ]]; then
		echo "WORKLOAD env varibale must be defined" >&2
		exit 2
	fi
	local WORKLOAD_FILE="${YCSB_HOME}/${WORKLOAD}"
	if [ ! -f "${WORKLOAD_FILE}" ]; then
		echo "${WORKLOAD} could not be found among the available workloads" >&2
		echo "Available workloads are: $(find "${YCSB_HOME}/workloads" -type f -print0)" >&2
		exit 3
	fi
	if [[ -z "${PROXY_PORT_8080_TCP_ADDR}" ]]; then
		echo "PROXY_PORT_8080_TCP_ADDR en variable must be defined" >&2
		exit 4
	fi

	if [[ -z "${PROXY_PORT_8080_TCP_PORT}" ]]; then
		echo "PROXY_PORT_8080_TCP_PORT en variable must be defined" >&2
		exit 5
	fi
}

#############################################################################
# wait_for_proxy
#
# Wait for the proxy to be able to receive connections by probing its expected
# open port every second for DEFAULT_TIMEOUT_IN_SECONDS seconds.
#############################################################################
function wait_for_proxy {
  local TIMER="${DEFAULT_TIMEOUT_IN_SECONDS}"
  while [[ "${TIMER}" -gt 0 ]]; do
    nc -w 1 "${PROXY_PORT_8080_TCP_ADDR}" "${PROXY_PORT_8080_TCP_PORT}" </dev/null
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

function ycsb_main {
	ycsb_check_variables
	# Create directory to collect the results
	mkdir -p /opt/ycsb
	# Need to move to the YCSB directory to access the contextual files such as the properties file
	cd "${YCSB_HOME}"
	wait_for_proxy
	bin/ycsb run playcloud -s -P "${WORKLOAD}" -p "playcloud.host=${PROXY_PORT_8080_TCP_ADDR}" -p "playcloud.port=${PROXY_PORT_8080_TCP_PORT}" > /opt/ycsb/run.txt 2> /opt/ycsb/run_noise.txt
	chmod 0777 -R /opt/ycsb/
}


if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  ycsb_main "$@"
fi
