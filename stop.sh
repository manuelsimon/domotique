#!/bin/bash
cd /home/pi/domotique/
pid=`cat start.pid`
echo "kill process $pid"
kill $pid
rm start.pid