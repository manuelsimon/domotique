#!/bin/bash
cd /home/pi/domotique/
isRunning=`./isRunning.sh`
if [[ isRunning -eq 0 ]]
then
	logger "Starting"
	# Attendre 25 secondes que le serveur mysql démarre
	sleep 25
	nohup ./releverTeleinfo.py 1 2 &
	start_pid=$!
	echo "$start_pid" > start.pid
	nohup ./releverTemperatures.py &
else
	echo "Already start"
fi
