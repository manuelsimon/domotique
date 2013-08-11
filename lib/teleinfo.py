#!/usr/bin/python
# -*- coding: utf-8 -*-
# Samuel Buffet samuel DOT buffet AT gmail DOT com
#
# Prototype d'utilisation du "Modem Téléinformation EDF - 2 compteurs"
# Ce modem est commercialisé par le site "http://www.planete-domotique.com"
#
# Sous Ubuntu (testé avec Karmic) vous devez ajouter une règle udev
# pour que le convertisseur serie/usb du module fonctionne
# sous etc/udev/rules.d  créez un nouveau fichier "teleinfoftdi.rules"
#
#       # USB-Serial Converter FTDI
#       ATTR{idVendor}=="0403", ATTR{idProduct}=="6001", MODE="660", GROUP="dialout"
#
# vous devez ensuite installer la lib python-ftdi (sudo apt-get install python-ftdi)
#
# Et voilà c'est pas fini mais avec ça vous devriez pouvoir finir.
# http://www.touteladomotique.com/forum/viewtopic.php?t=4355
# https://bitbucket.org/rhumland/teleinfo/src/2875e8583f81/teleinfocatcher.py
# http://www.neufbox4.org/wiki/index.php?title=T%C3%A9l%C3%A9information_compteur_%C3%A9lectrique
# http://www.erdfdistribution.fr/medias/DTR_Racc_Comptage/ERDF-NOI-CPT_02E.pdf
# http://www.planete-domotique.com/blog/2010/03/30/la-teleinformation-edf/

import ftdi
import time
import sys
import json
import datetime
import logging

CAR_SP=0x20 # SPace
CAR_NBSP=0xa0 # Non Breakable SPace
CAR_STX=0x02 # Start TeXt
CAR_ETX=0x03 # End TeXt
CAR_LF=0x0a # Line Feed
CAR_CR=0x0d # Carriage Return

# Disponible toutes options tarifaires
ADCO="ADCO" # Adresse du concentrateur de téléreport, 12 car
OPTARIF="OPTARIF" #Option tarifaire choisie, 4 car
	# BASE: Option Base, HC..: Option Heures Creuses, EJP.: Option EJP, BBRx: Option Tempo. x est un caractère ASCII imprimable qui reflète les programmes de commande des circuits de sortie à contacts auxiliaires du compteur
ISOUSC="ISOUSC" # Intensité souscrite, 2 car, unité A
PAPP="PAPP" # Puissance apparente, 5 car, unité VA
IINST="IINST" # Intensité Instantanée, 3 car, unité A
IMAX="IMAX" # Inténsité maximale appelée, 3 car, unité A
PTEC="PTEC" #Période Tarifaire en cours, 4 car
	# TH.. => Toutes les Heures.
	# HC.. => Heures Creuses.
	# HP.. => Heures Pleines.
	# HN.. => Heures Normales.
	# PM.. => Heures de Pointe Mobile.
	# HCJB => Heures Creuses Jours Bleus.
	# HCJW => Heures Creuses Jours Blancs (White).
	# HCJR => Heures Creuses Jours Rouges.
	# HPJB => Heures Pleines Jours Bleus.
	# HPJW => Heures Pleines Jours Blancs (White).
	# HPJR => Heures Pleines Jours Rouges.
MOTDETAT="MOTDETAT" # Mot d'état du compteur, 6 car

# Disponible uniquement option Base
BASE="BASE" # Index option Base, 8 car, unité Wh

# Disponible uniquement option Heure creuse
HCHC="HCHC" # Index Heures Creuses, 8 car, unité Wh
HCHP="HCHP" # Index Heures Pleines, 8 car, unité Wh
HHPHC="HHPHC" # Horaire Heures Pleines Heures Creuses, 1 car (A, C, D, E ou Y selon programmation du compteur)

BBRHCJB="BBRHCJB" # Heures Creuses Jours Bleus, 9 car, unité Wh
BBRHPJB="BBRHPJB" # Heures Pleines Jours Bleus, 9 car, unité Wh
BBRHCJW="BBRHCJW" # Heures Creuses Jours Blancs, 9 car, unité Wh
BBRHPJW="BBRHPJW" # Heures Pleines Jours Blancs, 9 car, unité Wh
BBRHCJR="BBRHCJR" # Heures Creuses Jours Rouges, 9 car, unité Wh
BBRHPJR="BBRHPJR" # Heures Pleines Jours Rouges, 9 car, unité Wh
DEMAIN="DEMAIN" # Couleur du lendemain {BLEU, BLAN, ROUG}

PORT_1  = 0x11
PORT_2  = 0x22
NO_PORT = 0x00

def ouvrirPort(port):
	# Création du context
	ftdiContext = ftdi.ftdi_context()

	# Initialisation du context
	if ftdi.ftdi_init(ftdiContext) < 0:
		raise IOError("Echec de l'initialisation")

	# Ouverture du port
	ret = ftdi.ftdi_usb_open(ftdiContext, 0x0403, 0x6001)
	if (ret) < 0:
		raise IOError("Impossible d'ouvrir le port " + hex(port) + " : " + repr(ret) + "(" + ftdi.ftdi_get_error_string(ftdiContext) + ")")


	# Fixer le debit à 1200 bit/s => 150 car/s (8 bits/car)
	ret = ftdi.ftdi_set_baudrate(ftdiContext, 1200)
	if (ret) < 0:
		raise IOError("Impossible de fixer le baudrate pour le port " + hex(port) + " : " + repr(ret) + "(" + ftdi.ftdi_get_error_string(ftdiContext) + ")")

	# Pour une obscure raison pour le moment il faut mettre ftdi.BITS_8
	# et non ftdi.BITS_7 comme indiqué dans la spec pour que cela fonctionne ???
	ret = ftdi.ftdi_set_line_property(ftdiContext, ftdi.BITS_8, ftdi.EVEN, ftdi.STOP_BIT_1)

	# Activation du compteur 1 et lecture de qqes trames
	ret = ftdi.ftdi_set_bitmode(ftdiContext, port, ftdi.BITMODE_CBUS);

	# Fixer le timeout de lecture
	ftdiContext.usb_read_timeout = 50000; 

	return ftdiContext

def fermerPort(ftdiContext):
	# Exemple de desactivation des compteurs
	ftdi.ftdi_set_bitmode(ftdiContext, NO_PORT, ftdi.BITMODE_CBUS);

	ret = ftdi.ftdi_usb_close(ftdiContext)
	if ret < 0:
		raise IOError("Impossible de fermer le port : " + repr(ret) + "(" + ftdi.ftdi_get_error_string(ftdiContext) + ")")

	ftdi.ftdi_deinit(ftdiContext);

	del ftdiContext

def getTrame(ftdiContext):
	# Récupérer une trame
	buf=' '
	startCapture = False
	stopCapture = False
	trame = []
	while not stopCapture:
		f = ftdi.ftdi_read_data(ftdiContext, buf, 0x1)
		if f != 0:
			ordBuf = ord(buf) & 0x07f
			if ordBuf == CAR_STX:
				startCapture = True
			if startCapture and ordBuf == CAR_ETX:
				stopCapture = True
			if startCapture:
				trame.append(ordBuf)
		time.sleep(0.01)
		
	return trame;

def afficherTrame(trame):
	# Afficher la trame brute
	lineHexa=""
	lineString=""
	print "Longueur de la trame : " + str(len(trame))
	nbCarParLigne = 16
	for i in range(0, len(trame)):
		ordBuf = trame[i]
		lineHexa += ('%02X' % ordBuf)
		lineHexa += unichr(0x20)
		if ((i + 1) % 8 == 0):
			lineHexa += unichr(0x20)

		if ordBuf > 0xA0:
			strCar = "."
		elif ordBuf < 0x20 :
			if ordBuf == CAR_STX:
				strCar = '\033[1m' + chr(ordBuf) + '\033[0m'
			elif ordBuf == CAR_ETX:
				strCar = '\033[1m' + chr(ordBuf) + '\033[0m'
			else:
				strCar = "."
		else:
			strCar = unichr(ordBuf)
		lineString += strCar #.rjust(5)
		if (((i + 1) % nbCarParLigne == 0) or i == len(trame) - 1):
			print lineHexa.ljust(nbCarParLigne * 3 + 2) + "| " + lineString
			lineString=""
			lineHexa=""

def trameToObj(trame):
	# Obtenir la trame sous la forme d'un objet
	trameObj={}
	trameObj[ADCO] = None
	trameObj[OPTARIF] = None
	trameObj[ISOUSC] = None
	trameObj[PAPP] = None
	trameObj[IINST] = None
	trameObj[IMAX] = None
	trameObj[PTEC] = None
	trameObj[BASE] = None
	trameObj[HCHC] = None
	trameObj[HCHP] = None
	trameObj[HHPHC] = None
	trameObj[BBRHCJB] = None
	trameObj[BBRHPJB] = None
	trameObj[BBRHCJW] = None
	trameObj[BBRHPJW] = None
	trameObj[BBRHCJR] = None
	trameObj[BBRHPJR] = None
	trameObj[DEMAIN] = None

	try:
		trame.pop(0) # Supprimer le caractere de début CAR_STX
		trame.pop(len(trame) - 1) # Supprimer le caractere de fin CAR_ETX
		while len(trame) != 0:
			controleCalcule=0
			trame.pop(0) # Supprimer le caractere de debut de groupe CAR_LF
			etiquette=""
			while trame[0] != CAR_SP:
				etiquette += unichr(trame[0])
				controleCalcule += trame.pop(0)
			controleCalcule += trame.pop(0) # Supprimer l'espace entre l'étiquette et la donnée
			donnee=""
			while trame[0] != CAR_SP:
				donnee += unichr(trame[0])
				controleCalcule += trame.pop(0)
			trame.pop(0)
			controle=trame.pop(0)

			trame.pop(0) # Supprimer le caractere de fin de groupe CAR_CR
			trameObj[etiquette] = donnee

			controleCalcule = ( controleCalcule & int("111111", 2) ) + 0x20
			if controleCalcule != controle:
				logging.error("Erreur de controle de la trame de teleinfo")
				trameObj = None
				break
	except:
		trameObj = None

	return trameObj

