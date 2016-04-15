#! /bin/bash

#	Measures the ping of a storage provider

ips=("204.79.197.213" "www.googleapis.com" "content.dropboxapi.com")
names=("onedrive" "gdrive" "dropbox")


for ((i=0; i<${#ips[*]}; i++));
do
	
	fping ${ips[i]} -C 100 -q >> ${names[i]}.txt 2>&1
	python provider_ping.py ${names[i]}.txt

done

