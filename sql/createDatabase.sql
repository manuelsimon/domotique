CREATE TABLE IF NOT EXISTS RELEVE_TEMPERATURE(
	date DATETIME PRIMARY KEY,
	sonde VARCHAR(100) NOT NULL,
	temperature DOUBLE NOT NULL
);

CREATE TABLE IF NOT EXISTS RELEVE_CONSOMMATION (
	date DATETIME PRIMARY KEY,
	ADCO char(12) COMMENT 'Adresse du concentrateur de téléreport, 12 car',
	OPTARIF char(4) COMMENT 'Option tarifaire choisie, 4 car. BASE: Option Base, HC..: Option Heures Creuses, EJP.: Option EJP, BBRx: Option Tempo. x est un caractère ASCII imprimable qui reflète les programmes de commande des circuits de sortie à contacts auxiliaires du compteur',
	ISOUSC tinyint COMMENT 'Intensité souscrite, 2 car, unité A',
	PAPP smallint COMMENT 'Puissance apparente, 5 car, unité VA',
	IINST tinyint COMMENT 'Intensité Instantanée, 3 car, unité A',
	IMAX tinyint COMMENT 'Inténsité maximale appelée, 3 car, unité A',
	PTEC char(4) COMMENT 'Période Tarifaire en cours, 4 car, TH..: Toutes les Heures, HC..: Heures Creuses, HP..: Heures Pleines, HN..: Heures Normales, PM..: Heures de Pointe Mobile, HCJB: Heures Creuses Jours Bleus, HCJW: Heures Creuses Jours Blancs (White), HCJR: Heures Creuses Jours Rouges, HPJB: Heures Pleines Jours Bleus, HPJW: Heures Pleines Jours Blancs (White), HPJR: Heures Pleines Jours Rouges.',

	BASE int COMMENT 'Index option Base, 8 car, unité Wh',

	HCHC int COMMENT 'Index Heures Creuses, 8 car, unité Wh',
	HCHP int COMMENT 'Index Heures Pleines, 8 car, unité Wh',
	HHPHC char(1) COMMENT 'Horaire Heures Pleines Heures Creuses, 1 car (A, C, D, E ou Y selon programmation du compteur)',

	BBRHCJB int COMMENT 'Heures Creuses Jours Bleus, 9 car, unité Wh',
	BBRHPJB int COMMENT 'Heures Pleines Jours Bleus, 9 car, unité Wh',
	BBRHCJW int COMMENT 'Heures Creuses Jours Blancs, 9 car, unité Wh',
	BBRHPJW int COMMENT 'Heures Pleines Jours Blancs, 9 car, unité Wh',
	BBRHCJR int COMMENT 'Heures Creuses Jours Rouges, 9 car, unité Wh',
	BBRHPJR int COMMENT 'Heures Pleines Jours Rouges, 9 car, unité Wh',
	DEMAIN char(4) COMMENT 'Couleur du lendemain, 4 car, {BLEU, BLAN, ROUG}',

	INDEX ADCO (ADCO),
	INDEX OPTARI (OPTARIF),
	INDEX PTEC (PTEC),
	INDEX HHPHC (HHPHC)
);


