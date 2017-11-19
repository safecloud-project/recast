#! /usr/bin/env bash


for i in $(seq 3 5); do
	scp docker-compose.yml 172.16.0.138:playcloud/
	scp dispatcher.json 172.16.0.138:playcloud/pyproxy/
	cd "${i}"
	echo "${PWD}"
	ssh -o "StrictHostKeyChecking no" 172.16.0.138 "cd playcloud && docker-compose stop && docker-compose rm -fv && docker-compose build && ./deploy_redis.sh ./ips.txt && docker-compose up -d && sleep 12"
	../../../../../clients/ab_playcloud.sh 1000 4 1 172.16.0.138:3000 > out.txt
	cd "${OLDPWD}"
done
