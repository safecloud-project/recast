#! /usr/bin/env bash
################################################################################
# A script that installs the basic dependencies for playcloud on a Ubuntu
# machine.
# Tested on Ubuntu 16.04 (xenial)
################################################################################

install_docker() {
	which docker > /dev/null
	if [[ "${?}" -ne 0 ]]; then
		sudo apt-get update && sudo apt-get install apt-transport-https ca-certificates curl software-properties-common --assume-yes && \
		curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -&& sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" && \
		sudo apt-get update && sudo apt-get install docker-ce --assume-yes
	fi
	local current_user="$(whoami)"
	groups "${current_user}" | grep -q "docker"
	if [[ "${?}" -ne 0 ]]; then
		sudo usermod "${current_user}" -aG docker
	fi
}

install_docker_compose() {
	which docker-compose > /dev/null
	if [[ "${?}" -ne 0 ]]; then
		sudo curl -L "https://github.com/docker/compose/releases/download/1.17.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
		sudo chmod +x /usr/local/bin/docker-compose
	fi
}

install_tools() {
	sudo apt-get update && \
	sudo apt-get dist-upgrade --assume-yes && \
	sudo apt-get install apache2-utils curl python-dev python-pip wget --assume-yes && \
	sudo apt-get autoremove --assume-yes && \
	LC_ALL=C pip install --upgrade pip && \
	LC_ALL=C pip install configparser docker ruamel.yaml requests
}

main() {
	install_docker
	install_docker_compose
	install_tools
	# Cleanup the system
	docker system prune --force
}
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
	main
fi
