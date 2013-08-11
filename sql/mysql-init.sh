#!/bin/bash
sudo kill `sudo cat /var/run/mysqld/mysqld.pid`
sleep 10
sudo mysqld_safe --init-file=/home/pi/domotique/sql/mysql-init.sql &
