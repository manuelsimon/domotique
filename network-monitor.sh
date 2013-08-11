#!/bin/bash

if ifconfig wlan0 | grep -q "inet addr:" ; then
  echo "Network connection up!"
else
  logger "Network connection down! Attempting reconnection."
  sudo ifdown --force wlan0
  sleep 10
  sudo ifup --force wlan0
fi
