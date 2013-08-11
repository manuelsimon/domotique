import MySQLdb
import datetime
import logging

def addWhereClause(whereClauses, clause):
	if (whereClauses is None):
		whereClauses = " WHERE "
	else:
		whereClauses += " AND "
	whereClauses += clause
	return whereClauses;

def getTemperaturesWhereClause(dateMin, dateMax, sonde):
	return getWhereClause([
		{'field':'date', 'op': '>=', 'expr': "'{}'", 'value': dateMin},
		{'field':'date', 'op': '<=', 'expr': "'{}'", 'value': dateMax},
		{'field':'sonde ', 'op': 'LIKE', 'expr': "'%{}%'", 'value': sonde}
	])
	
def getTemperaturesGroup(group, dateMin, dateMax, sonde):
	db = MySQLdb.connect(host="localhost", db="test")
	cur = db.cursor()

	query="SELECT date, sonde, temperature FROM RELEVE_TEMPERATURE"
	query = query + getWhereClause([
		{'field':'date', 'op': '>=', 'expr': "'{}'", 'value': dateMin},
		{'field':'date', 'op': '<=', 'expr': "'{}'", 'value': dateMax},
		{'field':'sonde ', 'op': 'LIKE', 'expr': "'%{}%'", 'value': sonde}
	])
	
	query = query + " and temperature = (select " + group + "(temperature) FROM RELEVE_TEMPERATURE " + getTemperaturesWhereClause(dateMin, dateMax, sonde) + ")"

	logging.debug("Execute query: <" + query + ">")
	cur.execute(query)
	releves=fetchallTo(cur, [
		{'name': 'date', 'type': 'datetime'},
		{'name': 'sonde', 'type': 'string'},
		{'name': 'temperature', 'type': 'float'}
	]);


	cur.close()
	db.close()
	
	return releves	

def getTemperature(sonde):
	db = MySQLdb.connect(host="localhost", db="test")
	cur = db.cursor()

	query="select date, temperature from RELEVE_TEMPERATURE WHERE date=(select max(date) from RELEVE_TEMPERATURE WHERE sonde='" + sonde +"') and sonde='" + sonde + "'"

	logging.debug("Execute query: <" + query + ">")
	cur.execute(query)
	row=cur.fetchone()
	dateStr = str(row[0])
	date=datetime.datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S")
	temperature=float(row[1])

	cur.close()
	db.close()
	
	return {'date': date, 'temperature': temperature}
	
def getTemperaturesAvg(dateMin, dateMax, sonde):
	db = MySQLdb.connect(host="localhost", db="test")
	cur = db.cursor()

	query="SELECT avg(temperature) FROM RELEVE_TEMPERATURE"
	query = query + getTemperaturesWhereClause(dateMin, dateMax, sonde)
	
	logging.debug("Execute query: <" + query + ">")
	cur.execute(query)
	row=cur.fetchone()
	temperature=float(row[0])

	cur.close()
	db.close()
	
	return temperature	

def getTemperaturesMinMaxAvg(dateMin, dateMax, sonde):
	mins = getTemperaturesGroup("min", dateMin, dateMax, sonde)
	maxs = getTemperaturesGroup("max", dateMin, dateMax, sonde)
	avg = getTemperaturesAvg(dateMin, dateMax, sonde)
	
	return {'mins': mins, 'maxs': maxs, 'avg': avg}
	
def getTemperatures(dateMin, dateMax, sonde):
	db = MySQLdb.connect(host="localhost", db="test")
	cur = db.cursor()

	query="SELECT date, sonde, temperature FROM RELEVE_TEMPERATURE"
	query = query + getTemperaturesWhereClause(dateMin, dateMax, sonde)

	logging.debug("Execute query: <" + query + ">")
	cur.execute(query)
	releves=fetchallTo(cur, [
		{'name': 'date', 'type': 'datetime'},
		{'name': 'sonde', 'type': 'string'},
		{'name': 'temperature', 'type': 'float'}
	]);

	cur.close()
	db.close()
	
	return releves


def getWhereClause(clauses):
	queryWhereClause = None;
	for clause in clauses:
		if clause['value'] != None:
			queryWhereClause = addWhereClause(queryWhereClause,  clause['field'] + " " + clause['op'] + " " + clause['expr'].format(clause['value']))

	if queryWhereClause == None:
		queryWhereClause = ""

	return queryWhereClause;

def fetchallTo(cur, returnMapping):
	releves=[]
	for row in cur.fetchall() :
		i=0 
		releve = {}
		for mapping in returnMapping:
			val = None
			if (row[i] != None):
				if (mapping['type'] == 'date'):
					valStr = str(row[i])
					pattern = "%Y-%m-%d"
					if ('pattern' in mapping and mapping['pattern'] is not None):
						pattern = mapping['pattern']
					val = datetime.datetime.strptime(valStr, pattern)
				elif (mapping['type'] == 'datetime'):
					valStr = str(row[i])
					val = datetime.datetime.strptime(valStr, "%Y-%m-%d %H:%M:%S")
				elif (mapping['type'] == 'int'):
					val = int(row[i])
				elif (mapping['type'] == 'float'):
					val = float(row[i])
				else: 
					val = str(row[i])
			releve[mapping['name']] = val;
			i = i + 1
		releves.append(releve)
	
	return releves

def getPuissanceApparente(dateMin, dateMax, adco):
	db = MySQLdb.connect(host="localhost", db="test")
	cur = db.cursor()

	query="SELECT date, ADCO, PAPP, IINST, PTEC FROM RELEVE_CONSOMMATION"
	query = query + getWhereClause([
		{'field':'date', 'op': '>=', 'expr': "'{}'", 'value': dateMin},
		{'field':'date', 'op': '<=', 'expr': "'{}'", 'value': dateMax},
		{'field':'ADCO', 'op': 'LIKE', 'expr': '%{}%', 'value': adco},
		{'field':'PAPP', 'op': 'IS', 'expr': "{}", 'value': 'NOT NULL'}
	])

	logging.debug("Execute query: <" + query + ">")
	cur.execute(query)
	releves=fetchallTo(cur, [
		{'name': 'date', 'type': 'datetime'},
		{'name': 'acdo', 'type': 'string'},
		{'name': 'papp', 'type': 'int'},
		{'name': 'iinst', 'type': 'int'},
		{'name': 'ptec', 'type': 'string'}
	]);

	cur.close()
	db.close()
	
	return releves

# Voir pb ADCO null 
def getConsommationBase(dateMin, dateMax, adco, intervalle):
	if (intervalle == "heure"):
		groupByDatePattern = '%Y-%m-%d %H'
		datePattern = '%Y-%m-%d %H'
	elif (intervalle == "jour" or intervalle is None):
		groupByDatePattern = '%Y-%m-%d'
		datePattern = '%Y-%m-%d'
	elif (intervalle == "semaine"):
		groupByDatePattern = '%Y-%u'
		datePattern = '%Y-%W'
	elif (intervalle == "mois"):
		groupByDatePattern = '%Y-%m'
		datePattern = '%Y-%m'
	elif (intervalle == "annee"):
		groupByDatePattern = '%Y'
		datePattern = '%Y'
	
	db = MySQLdb.connect(host="localhost", db="test")
	cur = db.cursor()

	query = "select DATE_FORMAT(date, '" + groupByDatePattern + "'), ADCO"
	query = query + ", max(BASE) - min(BASE)"
	query = query + " from RELEVE_CONSOMMATION"
	query = query + getWhereClause([
		{'field':'date', 'op': '>=', 'expr': "'{}'", 'value': dateMin},
		{'field':'date', 'op': '<=', 'expr': "'{}'", 'value': dateMax},
		{'field':'ADCO', 'op': 'LIKE', 'expr': "'%{}%'", 'value': adco},
		{'field':'ADCO', 'op': 'IS', 'expr': '{}', 'value': 'NOT NULL'},
		{'field':'OPTARIF', 'op': 'LIKE', 'expr': "'{}%'", 'value': 'BASE'},
		{'field':'PTEC', 'op': 'IS', 'expr': '{}', 'value': 'NOT NULL'}
	])
	query = query + " group by DATE_FORMAT(date, '" + groupByDatePattern + "'), ADCO"

	logging.debug("Execute query: <" + query + ">")
	cur.execute(query)
	releves=fetchallTo(cur, [
		{'name': 'date', 'type': 'date', 'pattern': datePattern},
		{'name': 'acdo', 'type': 'string'},
		{'name': 'base', 'type': 'int'}
	]);

	cur.close()
	db.close()
	
	return releves

def getConsommationHC(dateMin, dateMax, adco):
	db = MySQLdb.connect(host="localhost", db="test")
	cur = db.cursor()

	query="select DATE_FORMAT(date, '%Y-%m-%d'), max(HCHC) - min(HCHC), max(HCHP)-min(HCHP) from RELEVE_CONSOMMATION"
	query = query + getWhereClause([
		{'field':'date', 'op': '>=', 'expr': "'{}'", 'value': dateMin},
		{'field':'date', 'op': '<=', 'expr': "'{}'", 'value': dateMax},
		{'field':'ADCO', 'op': 'LIKE', 'expr': "'%{}%'", 'value': adco},
		{'field':'ADCO', 'op': 'IS', 'expr': '{}', 'value': 'NOT NULL'},
		{'field':'OPTARIF', 'op': 'LIKE', 'expr': "'{}%'", 'value': 'HC'},
		{'field':'PTEC', 'op': 'IS', 'expr': '{}', 'value': 'NOT NULL'}
	])
	query = query + " group by DATE_FORMAT(date, '%Y%m%d'), ADCO"

	logging.debug("Execute query: <" + query + ">")
	cur.execute(query)
	releves=fetchallTo(cur, [
		{'name': 'date', 'type': 'date'},
		{'name': 'acdo', 'type': 'string'},
		{'name': 'hchc', 'type': 'int'},
		{'name': 'hchp', 'type': 'int'}
	]);

	cur.close()
	db.close()
	
	return releves
#
# Par heure, jour
# Par semaine
# Par mois
# Par anne
def getConsommationTempo(dateMin, dateMax, adco, intervalle):
	if (intervalle == "heure"):
		groupByDatePattern = '%Y-%m-%d %H'
		datePattern = '%Y-%m-%d %H'
	elif (intervalle == "jour" or intervalle is None):
		groupByDatePattern = '%Y-%m-%d'
		datePattern = '%Y-%m-%d'
	elif (intervalle == "semaine"):
		groupByDatePattern = '%Y-%u'
		datePattern = '%Y-%W'
	elif (intervalle == "mois"):
		groupByDatePattern = '%Y-%m'
		datePattern = '%Y-%m'
	elif (intervalle == "annee"):
		groupByDatePattern = '%Y'
		datePattern = '%Y'
	
	db = MySQLdb.connect(host="localhost", db="test")
	cur = db.cursor()

	query="select DATE_FORMAT(date, '" + groupByDatePattern + "'), ADCO"
#	query = query + ", COALESCE(max(HCHC), 0) + COALESCE(max(BBRHCJB), 0) + COALESCE(max(BBRHCJW), 0) + COALESCE(max(BBRHCJR), 0)"
#	query = query + "- (COALESCE(min(HCHC), 0) + COALESCE(min(BBRHCJB), 0) + COALESCE(min(BBRHCJW), 0) + COALESCE(min(BBRHCJR), 0))"
#	query = query + ", COALESCE(max(HCHP), 0) + COALESCE(max(BBRHPJB), 0) + COALESCE(max(BBRHPJW), 0) + COALESCE(max(BBRHPJR), 0)"
#	query = query + "- (COALESCE(min(HCHP), 0) + COALESCE(min(BBRHPJB), 0) + COALESCE(min(BBRHPJW), 0) + COALESCE(min(BBRHPJR), 0)) from RELEVE_CONSOMMATION"
	query = query + ", COALESCE(max(BBRHCJB), 0) - COALESCE(min(BBRHCJB), 0)"
	query = query + ", COALESCE(max(BBRHPJB), 0) - COALESCE(min(BBRHPJB), 0)"
	query = query + ", COALESCE(max(BBRHCJW), 0) - COALESCE(min(BBRHCJW), 0)"
	query = query + ", COALESCE(max(BBRHPJW), 0) - COALESCE(min(BBRHPJW), 0)"
	query = query + ", COALESCE(max(BBRHCJR), 0) - COALESCE(min(BBRHCJR), 0)"
	query = query + ", COALESCE(max(BBRHPJR), 0) - COALESCE(min(BBRHPJR), 0)"
	query = query + " from RELEVE_CONSOMMATION"
	
	query = query + getWhereClause([
		{'field':'date', 'op': '>=', 'expr': "'{}'", 'value': dateMin},
		{'field':'date', 'op': '<=', 'expr': "'{}'", 'value': dateMax},
		{'field':'ADCO', 'op': 'LIKE', 'expr': "'%{}%'", 'value': adco},
		{'field':'ADCO', 'op': 'IS', 'expr': '{}', 'value': 'NOT NULL'},
		{'field':'OPTARIF', 'op': 'LIKE', 'expr': "'{}%'", 'value': 'BBR'},
		{'field':'PTEC', 'op': 'IS', 'expr': '{}', 'value': 'NOT NULL'}
	])
	
	query = query + " group by DATE_FORMAT(date, '" + groupByDatePattern + "'), ADCO"

	logging.debug("Execute query: <" + query + ">")
	cur.execute(query)
	releves=fetchallTo(cur, [
		{'name': 'date', 'type': 'date', 'pattern': datePattern},
		{'name': 'acdo', 'type': 'string'},
		{'name': 'hcjb', 'type': 'int'},
		{'name': 'hpjb', 'type': 'int'},
		{'name': 'hcjw', 'type': 'int'},
		{'name': 'hpjw', 'type': 'int'},
		{'name': 'hcjr', 'type': 'int'},
		{'name': 'hpjr', 'type': 'int'}
	]);

	cur.close()
	db.close()
	
	return releves
