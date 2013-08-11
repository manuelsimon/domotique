#!/usr/bin/python
import sys
sys.path.append("..")
from lib import repository

#releves = repository.getPuissanceApparente("2013-08-01", None, None)
#print repository.getConsommationBase("2013-01-04 08:00:00", "2013-08-04 10:00:00", None, None)
#for intervalle in ["semaine", "mois", "annee"]:
for intervalle in ["jour", "semaine", "mois", "annee"]:
	print "----------"
	releves = repository.getConsommationBase("2013-08-03 08:00:00", None, None, intervalle)
	object = releves
	for property in object:
		print property
