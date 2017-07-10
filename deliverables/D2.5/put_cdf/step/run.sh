#! /usr/bin/env bash


for i in $(seq 3 5); do
	cd "${i}"
	echo "${PWD}"
	ssh -o "StrictHostKeyChecking no" 172.16.0.85 "cd playcloud && docker-compose stop && docker-compose rm -fv && docker-compose build && ./deploy_redis.sh && docker-compose up -d && sleep 12"
	../../../clients/ab_playcloud.sh 1000 4 1 172.16.0.85:3000 > out.txt
	cd "${OLDPWD}"
done
