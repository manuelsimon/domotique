#!/usr/bin/python
# datademo.py 
# a simple script to pull some data from MySQL

import json
import time
import datetime
import cgi
import math
from lib import repository

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
		date1erJanvier1970=datetime.datetime(1970,1,1)
		nbMillisecondesDepuis1970 = long((obj-date1erJanvier1970).total_seconds() * 1000)
		return nbMillisecondesDepuis1970
	        #return json.JSONEncoder.default(self, obj)

#releves = getTemperatures(None, None, '28-0000048f')

form = cgi.FieldStorage()
typeReleve = form.getvalue('type')
if typeReleve == 'temperatures':
	releves = repository.getTemperatures(form.getvalue("dateMin"), form.getvalue("dateMax"), form.getvalue("idSonde"))
	print "Content-type: application/json\n\n";
	print json.dumps(releves, cls = MyEncoder)

elif typeReleve == 'temperaturesMinMaxAvg':
	releves = repository.getTemperaturesMinMaxAvg(form.getvalue("dateMin"), form.getvalue("dateMax"), form.getvalue("idSonde"))
	print "Content-type: application/json\n\n";
	print json.dumps(releves, cls = MyEncoder)

elif typeReleve == 'papp':
	releves = repository.getPuissanceApparente(form.getvalue("dateMin"), form.getvalue("dateMax"), form.getvalue("adco"))

	# Supprimer les releves identiques pour limiter la qte de donnees transmises
	i = 0
	while i < len(releves):
		precedentIdentique = (i > 0 and releves[i - 1]['papp'] == releves[i]['papp'])
		suivantIdentique = (i + 1 < len(releves) and releves[i + 1]['papp'] == releves[i]['papp'])
		if (precedentIdentique and suivantIdentique):
			releves.pop(i)
		else:
			i = i + 1

	print "Content-type: application/json\n\n";
	print json.dumps(releves, cls = MyEncoder)
	
elif typeReleve == 'consoHC':
	releves = repository.getConsommationHC(form.getvalue("dateMin"), form.getvalue("dateMax"), form.getvalue("adco"))
	print "Content-type: application/json\n\n";
	print json.dumps(releves, cls = MyEncoder)

elif typeReleve == 'consoTempo':
	releves = repository.getConsommationTempo(form.getvalue("dateMin"), form.getvalue("dateMax"), form.getvalue("adco"), form.getvalue("intervalle"))
	print "Content-type: application/json\n\n";
	print json.dumps(releves, cls = MyEncoder)

elif typeReleve == 'consoBase':
	releves = repository.getConsommationBase(form.getvalue("dateMin"), form.getvalue("dateMax"), form.getvalue("adco"), form.getvalue("intervalle"))
	print "Content-type: application/json\n\n";
	print json.dumps(releves, cls = MyEncoder)
	
#print repository.getTemperaturesMinMaxAvg(form.getvalue("dateMin"), form.getvalue("dateMax"), '28-0000048f')
#print repository.getTemperature('28-0000048f1c00')
