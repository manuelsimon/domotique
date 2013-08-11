#!/usr/bin/python
# -*- coding: utf-8 -*-

import locale
import logging
import time
import datetime
from lib import ds18b20

INTERVALLE_ENTRE_2_RELEVES_EN_MINUTES=10
nbMaxTentatives = 3
FORMAT = '%(asctime)-15s:%(levelname)s:%(message)s'
logging.basicConfig(format=FORMAT,level=logging.DEBUG)

logging.info("Initialisation")
ds18b20.init()

locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')

devicesName=ds18b20.getDevicesName()
nbDevices=len(devicesName)
if (nbDevices > 0):
	logging.info("Nombre de sondes : %s", nbDevices)
	while True:
		for deviceName in devicesName:
			nbTentatives = 0
			temperature = None
			while temperature is None and nbTentatives < nbMaxTentatives:
				temperature=ds18b20.getTemperature(deviceName)
				nbTentatives += 1
				
			if temperature is not None:
				now = datetime.datetime.now()
				ds18b20.insertTemperature(now, deviceName, temperature)
				logging.debug("Température de la sonde %s : %s", deviceName, temperature)
			else:
				logging.error("Température non récupérée pour la sonde %s : %s tentatives en echec", deviceName, nbMaxTentatives)

		#wait x seconds and repeat
		logging.debug("Prochain relevé dans %s minutes", INTERVALLE_ENTRE_2_RELEVES_EN_MINUTES)
		time.sleep(INTERVALLE_ENTRE_2_RELEVES_EN_MINUTES * 60)
else:
	logging.error("Aucune sonde de température")

exit(0)
