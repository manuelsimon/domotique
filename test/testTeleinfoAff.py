#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import time
import datetime
import teleinfo
import json
import MySQLdb
import sys

FORMAT = '%(asctime)-15s:%(levelname)s:%(message)s'
logging.basicConfig(format=FORMAT,level=logging.DEBUG)

portArgs = 1
if len(sys.argv) > 1:
	portArgs = sys.argv[1]
port = teleinfo.PORT_1
if int(portArgs) == 2:
	port = teleinfo.PORT_2
logging.info( "Port numero %s", port)
ftdiContext = teleinfo.ouvrirPort(port)
try:
	nbMaxTentatives = 3
	while True:
		startTime = datetime.datetime.now()
		logging.debug("Recuperation d'une trame de teleinfo");
		nbTentatives = 0
		trameObj = None
		while trameObj is None and nbTentatives < nbMaxTentatives:
			trame = teleinfo.getTrame(ftdiContext)
			teleinfo.afficherTrame(trame)
			trameObj = teleinfo.trameToObj(trame)
			nbTentatives += 1

		if trameObj != None:
			logging.debug("Trame récupérée en %s tentative(s)", nbTentatives)
			print json.dumps(trameObj)
		else:
			logging.error("Trame non récupérée : %s tentatives en echec", nbMaxTentatives)

		#wait x seconds and repeat
		time.sleep(30)
finally:
	logging.info("Fermeture du port");
	teleinfo.fermerPort(ftdiContext)

exit(0)
