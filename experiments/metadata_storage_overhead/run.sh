#! /usr/bin/env bash

################################################################################
# CONFIGURATION ################################################################
# Configuration files
readonly CONFIGS_TO_TEST=("./conf-1-10-3" "./conf-1-5-3" "./conf-5-2-7" "./conf-5-1-7")
readonly CONF_SETUP="./conf"
readonly COMPOSE_FILE="../../docker-compose.yml"
readonly COMPOSE_FILE_BACKUP="${COMPOSE_FILE}.bw.bak"
readonly DISPARCHER_FILE="../../pyproxy/dispatcher.json"
readonly DISPARCHER_FILE_BACKUP="${DISPARCHER_FILE}.bw.bak"
readonly PYCODER_FILE="../../pyproxy/pycoder.cfg"
readonly PYCODER_FILE_BACKUP="../../pyproxy/pycoder.cfg.bw.bak"

# Proxy setup
readonly DEFAULT_TIMEOUT_IN_SECONDS=60
readonly PROXY_HOST="127.0.0.1"
readonly PROXY_PORT=3000

# Experimental setup
readonly RESULTS_DIRECTORY="./results"
readonly RUNS=5
readonly NUMBER_OF_CORES="$(nproc --all)"
readonly STEPS=("0" "1" "10" "100" "1000" "10000")
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
  if [[ "${#}" -ne 1 ]]; then
    echo "Usage: setup_playcloud config_directory" >&2
    exit 0
  fi
  cp "${COMPOSE_FILE}" "${COMPOSE_FILE_BACKUP}"
  cp "${DISPARCHER_FILE}" "${DISPARCHER_FILE_BACKUP}"
  cp "${PYCODER_FILE}" "${PYCODER_FILE_BACKUP}"
  cp "${config_directory}/docker-compose.yml" "${COMPOSE_FILE}"
  cp "${config_directory}/pyproxy/dispatcher.json" "${DISPARCHER_FILE}"
  cp "${config_directory}/pyproxy/pycoder.cfg" "${PYCODER_FILE}"
  local volume_files=($(find ../../volumes -type f | sort | xargs))
  for vf in "${volume_files[@]}"; do
    local buvf="${vf}.bak"
    mv "${vf}" "${buvf}"
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
  local backed_up_volume_files=($(find ../../volumes -type f -iname "*.bak" | sort | xargs))
  for buvf in "${backed_up_volume_files[@]}"; do
    local vf="${buvf::-4}"
    mv "${buvf}" "${vf}"
  done
}

start_playcloud() {
  if [[ "${#}" -ne 1 ]]; then
    echo "Usage: start_playcloud config_directory" >&2
    exit 0
  fi
  local config_directory="${1}"
  docker-compose -f "${COMPOSE_FILE}" stop
  docker-compose -f "${COMPOSE_FILE}" rm -fv
  setup_playcloud "${config_directory}"
  docker-compose -f "${COMPOSE_FILE}" build
  docker-compose -f "${COMPOSE_FILE}" up -d
  wait_for_proxy
}

stop_playcloud() {
  docker-compose -f "${COMPOSE_FILE}" stop
  docker-compose -f "${COMPOSE_FILE}" rm -fv
  restore_playcloud
}

take_storage_overhead_snapshot() {
  if [[ "${#}" -ne 1 ]]; then
    echo "take_storage_overhead_snapshot output_file" >&2
    exit 1
  fi
  local destination="${1}"
  docker-compose -f "${COMPOSE_FILE}" exec  metadata redis-cli INFO memory > "${destination}"
  docker-compose -f "${COMPOSE_FILE}" exec  metadata redis-cli SAVE
  du -b ../../volumes/metadata/dump.rdb >> "${destination}"
  du -b ../../volumes/metadata/appendonly.aof >> "${destination}"
}

DATA_FILE="/tmp/storage_overhead_doc.txt"
base64 /dev/urandom | head  -c "64000" > "${DATA_FILE}"

mkdir -p "${RESULTS_DIRECTORY}"
for config in "${CONFIGS_TO_TEST[@]}"; do
  if [[ ! -d "${config}" ]]; then
    echo "Cannot find directory ${config}" >&2
    exit 0
  fi
  mkdir -p "${RESULTS_DIRECTORY}/${config}"
  for run in $(seq 1 "${RUNS}"); do
    mkdir -p "${RESULTS_DIRECTORY}/${config}/${run}"
    rm -f ../../volumes/metadata/dump.rdb
    rm -f ../../volumes/metadata/appendonly.aof
    start_playcloud "${config}"
    last_step="0"
    for step in "${STEPS[@]}"; do
      documents_to_insert=$((step - last_step))
      echo "Will now insert ${documents_to_insert} documents"
      ab -n "${documents_to_insert}" -u "${DATA_FILE}" "http://${PROXY_HOST}:${PROXY_PORT}/"
      take_storage_overhead_snapshot "${RESULTS_DIRECTORY}/${config}/${run}/${step}-info_memory.txt"
      last_step="${step}"
    done
    docker-compose -f "${COMPOSE_FILE}" exec  metadata redis-cli SAVE
    stop_playcloud "${config}"
    du -b ../../volumes/metadata/dump.rdb >> "${RESULTS_DIRECTORY}/${config}/${run}/final-info_memory.txt"
    rm -f ../../volumes/metadata/dump.rdb
    rm -f ../../volumes/metadata/appendonly.aof
  done
done
