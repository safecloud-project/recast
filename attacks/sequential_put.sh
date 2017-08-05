#! /usr/bin/env bash
###############################################################################
# A script that sequentially inserts small documents in playcloud
###############################################################################

run_experiment() {
	local files="${1:=1000000}"
	local file_size_in_bytes=512
	local folder="${PWD}/randfiles"
	mkdir --parents "${folder}"
	for index in $(seq "${files}"); do
		local path="${folder}/rand${index}.txt"
    dd if=/dev/urandom of="${path}" bs="${file_size_in_bytes}" count=1 2>/dev/null
		path=$(curl --silent -X PUT proxy:8000 -T "${path}" 2>&1)
		echo "Finished uploading ${path}"
	done
}


run_experiment ${@}