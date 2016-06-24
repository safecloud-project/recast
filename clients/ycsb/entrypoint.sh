#! /usr/bin/env bash

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
		echo "Available workloads are: $(find ${YCSB_HOME}/workloads -type f -print0)" >&2
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

function ycsb_main {
	ycsb_check_variables
	# Need to move to the YCSB directory to access the contextual files such as the properties file
	cd "${YCSB_HOME}"
	bin/ycsb load playcloud -s -P "${WORKLOAD}" -p "playcloud.host=${PROXY_PORT_8080_TCP_ADDR}" -p "playcloud.port=${PROXY_PORT_8080_TCP_PORT}"
	bin/ycsb run playcloud -s -P "${WORKLOAD}" -p "playcloud.host=${PROXY_PORT_8080_TCP_ADDR}" -p "playcloud.port=${PROXY_PORT_8080_TCP_PORT}"
}


if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  ycsb_main "$@"
fi
