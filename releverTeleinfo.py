#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import time
import datetime
from lib import teleinfo
import sys

import MySQLdb

FORMAT = '%(asctime)-15s:%(levelname)s:%(message)s'
logging.basicConfig(format=FORMAT,level=logging.DEBUG)

def insertTrameTeleinfo(time, trame):
	conn = MySQLdb.connect(host= "localhost",
					  db="test")
	x = conn.cursor()

	try:
	   x.execute("""INSERT INTO RELEVE_CONSOMMATION VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", 
		(time.strftime('%Y-%m-%d %H:%M:%S'), 
		trame[teleinfo.ADCO],
		trame[teleinfo.OPTARIF],
		trame[teleinfo.ISOUSC],
		trame[teleinfo.PAPP],
		trame[teleinfo.IINST],
		trame[teleinfo.IMAX],
		trame[teleinfo.PTEC],
		trame[teleinfo.BASE],
		trame[teleinfo.HCHC],
		trame[teleinfo.HCHP],
		trame[teleinfo.HHPHC],
		trame[teleinfo.BBRHCJB],
		trame[teleinfo.BBRHPJB],
		trame[teleinfo.BBRHCJW],
		trame[teleinfo.BBRHPJW],
		trame[teleinfo.BBRHCJR],
		trame[teleinfo.BBRHPJR],
		trame[teleinfo.DEMAIN]
		))
	   conn.commit()
	except Exception as e:
    		logging.error("Impossible d'insérer la trame de teleinfo : %s", e)
		conn.rollback()
		return False
	finally:
		conn.close()
	return True

def readTrameAndInsert(port): 
	ftdiContext = teleinfo.ouvrirPort(port)
	try:
		nbMaxTentatives = 3
		startTime = datetime.datetime.now()
		logging.debug("Recuperation d'une trame de teleinfo, port %s", hex(port));
		nbTentatives = 0
		trameObj = None
		while trameObj is None and nbTentatives < nbMaxTentatives:
			trame = teleinfo.getTrame(ftdiContext)
			trameObj = teleinfo.trameToObj(trame)
			nbTentatives += 1
		#afficherTrame(trame)

		if trameObj != None:
			logging.debug("Trame récupérée en %s tentative(s)", nbTentatives)
			#print json.dumps(trameObj)
			if insertTrameTeleinfo(startTime, trameObj):
				logging.debug("Trame de teleinfo insérée en base de données")
			else:
				logging.warning("Trame de teleinfo non insérée en base de données")
				
		else:
			logging.error("Trame non récupérée : %s tentatives en échec", nbMaxTentatives)

	finally:
		logging.info("Fermeture du port %s", hex(port));
		teleinfo.fermerPort(ftdiContext)

ports=[]
argsPorts = sys.argv;
programName=argsPorts[0]
del argsPorts[0] # Supprimer le nom du programme
if len(argsPorts) != 0:
	for i in range(len(argsPorts)):
		if int(argsPorts[i]) == 2:
			ports.append(teleinfo.PORT_2)
		else:
			ports.append(teleinfo.PORT_1)
		logging.info("Port numero %s : %s", argsPorts[i], hex(ports[i]))

	while True:
		for i in range(len(ports)):
			readTrameAndInsert(ports[i])
		#wait x seconds and repeat
		time.sleep(5)
else:
	logging.error("Syntaxe incorrecte, il faut préciser les ports à relever. Ex. : %s 1 2 ", programName)

exit(0)
