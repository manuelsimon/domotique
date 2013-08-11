#!/bin/bash
cd /home/pi/domotique/
if [ -f start.pid ]
then
	pid=`cat start.pid`
	ps -fu pi | grep `cat start.pid` | grep -v grep | wc -l
else
	echo 0
fi