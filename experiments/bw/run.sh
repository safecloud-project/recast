#! /usr/bin/env bash

################################################################################
# CONFIGURATION ################################################################
# Configuration files
readonly CONF_SETUP="./conf"
readonly COMPOSE_FILE="../../docker-compose.yml"
readonly COMPOSE_FILE_BACKUP="${COMPOSE_FILE}.bw.bak"
readonly COMPOSE_FILE_SETUP="${CONF_SETUP}/docker-compose.yml"
readonly DISPARCHER_FILE="../../pyproxy/dispatcher.json"
readonly DISPARCHER_FILE_BACKUP="${DISPARCHER_FILE}.bw.bak"
readonly DISPARCHER_FILE_SETUP="${CONF_SETUP}/pyproxy/dispatcher.json"
readonly PYCODER_FILE="../../pycoder/pycoder.cfg"
readonly PYCODER_FILE_BACKUP="../../pycoder/pycoder.cfg.bw.bak"
readonly PYCODER_FILE_SETUP="${CONF_SETUP}/pycoder/pycoder.cfg"

# Proxy setup
readonly DEFAULT_TIMEOUT_IN_SECONDS=60
readonly PROXY_HOST="127.0.0.1"
readonly PROXY_PORT=3000

# Experimental setup
readonly RESULTS_DIRECTORY="./results"
readonly RUNS=30
################################################################################

wait_for_proxy() {
  local TIMER="${DEFAULT_TIMEOUT_IN_SECONDS}"
  while [[ "${TIMER}" -gt 0 ]]; do
    nc -q 1 "${PROXY_HOST}" "${PROXY_PORT}" </dev/null
    if [[ "${?}" -eq 0 ]]; then
      break
    fi
    echo "waiting for proxy ...";
    TIMER=$(( TIMER - 1 ))
    sleep 1
  done

  if [[ "${TIMER}" -eq 0 ]]; then
    echo "Failed to connect to the proxy(${PROXY_HOST}:${PROXY_PORT}) after ${DEFAULT_TIMEOUT_IN_SECONDS} seconds"
    exit 1
  fi
}

setup_playcloud() {
  cp "${COMPOSE_FILE}" "${COMPOSE_FILE_BACKUP}"
  cp "${DISPARCHER_FILE}" "${DISPARCHER_FILE_BACKUP}"
  cp "${COMPOSE_FILE_SETUP}" "${COMPOSE_FILE}"
  cp "${DISPARCHER_FILE_SETUP}" "${DISPARCHER_FILE}"
  cp "${PYCODER_FILE_SETUP}" "${PYCODER_FILE}"
  local volume_files=("$(find ../../volumes -type f | sort | xargs)")
  for vf in ${volume_files[@]}; do
    local buvf="${vf}.bak"
    mv "${vf}" "${buvf}"
  done
  local volume_files=("$(find conf/volumes/ -type f | sort | xargs)")
  for vf in ${volume_files[@]}; do
    local destination_volume_file="$(echo ${vf} | sed 's/conf\//..\/..\//')"
    cp "${vf}" "${destination_volume_file}"
  done
}

restore_playcloud() {
  if [[ -f "${COMPOSE_FILE_BACKUP}" ]]; then
    mv "${COMPOSE_FILE_BACKUP}" "${COMPOSE_FILE}"
  fi
  if [[ -f "${DISPARCHER_FILE_BACKUP}" ]]; then
    mv "${DISPARCHER_FILE_BACKUP}" "${DISPARCHER_FILE}"
  fi
  if [[ -f "${PYCODER_FILE_BACKUP}" ]]; then
    mv "${PYCODER_FILE_BACKUP}" "${PYCODER_FILE}"
  fi
  local backed_up_volume_files=("$(find ../../volumes -type f -iname "*.bak" | sort | xargs)")
  for buvf in ${backed_up_volume_files[@]}; do
    local vf="${buvf::-4}"
    mv "${buvf}" "${vf}"
  done  
}

start_playcloud() {
  docker-compose -f "${COMPOSE_FILE}" stop
  docker-compose -f "${COMPOSE_FILE}" rm -fv
  setup_playcloud
  docker-compose -f "${COMPOSE_FILE}" build
  docker-compose -f "${COMPOSE_FILE}" up -d
  wait_for_proxy
}

stop_playcloud() {
  docker-compose -f "${COMPOSE_FILE}" stop
  docker-compose -f "${COMPOSE_FILE}" rm -fv
  restore_playcloud
}

take_network_snapshot() {
  if [[ "${#}" -ne 1 ]]; then
    echo "take_network_snapshot <output_file>" >&2
    exit 0
  fi
  local output_file="${1}"
  ../../scripts/traffic_counter.py > "${output_file}"
}

put_random_data() {
  if [[ "${#}" -ne 2 ]]; then
    echo "push_random_data <document name> <size in bytes>" >&2
    exit 0
  fi
  local document_name="${1}"
  local size_in_bytes="${2}"
  local random_file="/tmp/bw-${RANDOM}.txt"
  base64 /dev/urandom | head  -c "${size_in_bytes}" > "${random_file}"
  curl -X PUT "http://${PROXY_HOST}:${PROXY_PORT}/${document_name}" -T "${random_file}"
  rm "${random_file}"
}


delete_blocks() {
  docker-compose --file "${COMPOSE_FILE}" exec redis redis-cli DEL doc10-00
}

repair_blocks() {
  docker-compose --file "${COMPOSE_FILE}" exec proxy ./repair.py doc10-00
}

mkdir -p "${RESULTS_DIRECTORY}"

for run in $(seq 1 "${RUNS}"); do
  mkdir -p "${RESULTS_DIRECTORY}/${run}"
  start_playcloud
  # Delete blocks
  delete_blocks
  take_network_snapshot "${RESULTS_DIRECTORY}/${run}/bw-start-snapshot.json"
  # Repair block
  repair_blocks
  take_network_snapshot "${RESULTS_DIRECTORY}/${run}/bw-stop-snapshot.json"
  stop_playcloud
done

