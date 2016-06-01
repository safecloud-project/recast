#! /usr/bin/env bash

CONTAINER_NAME="macrorun_client"


function print_help {
	echo "Usage: macrorun.sh"
	echo ""
	echo "Run with macro level experiments while changing all configurations"
}

function build_container {
	local readonly CONTAINER_DIRECTORY="$(dirname ${BASH_SOURCE[0]})/clients"
	local readonly DOCKER_FILE="${CONTAINER_DIRECTORY}/macrorun.Dockerfile"
	docker build -f "${DOCKER_FILE}" -t "${CONTAINER_NAME}"  "${CONTAINER_DIRECTORY}"
}

function run_experiment {
	local readonly configuration_file="${1}"
	local readonly current_directory=$(dirname ${BASH_SOURCE[0]})
	local readonly destination_directory="$(realpath ${current_directory})/xpdata/macrorun/${configuration_file}"
	mkdir -p "${destination_directory}"
	docker-compose up -d --build
	docker run -it --rm --name "${CONTAINER_NAME}" --volume="${destination_directory}":/tmp/macrorun --link playcloud_proxy_1:proxy "${CONTAINER_NAME}"  test-load.sh
	docker-compose stop
	docker-compose rm -fv
}


function main {
	if [[ "${#}" -ne 0 ]]; then
		print_help
		exit 0
	fi
	build_container
	local configuration_files="$(find ./env -type f -iname "*.env" | xargs)"
	for configuration_file in ${configuration_files}; do
		run_experiment "${configuration_file}"
		exit 0
	done
}


main "${@}"
