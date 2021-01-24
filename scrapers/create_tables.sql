CREATE TABLE country(
	ccode TEXT,
	name TEXT,
	PRIMARY KEY (ccode)
);		

CREATE TABLE epi_score(
	ccode TEXT,
	rank INTEGER,
	score REAL,
	base_rank INTEGER,
	base_score REAL,
	PRIMARY KEY (ccode),
	FOREIGN KEY (ccode) REFERENCES country (ccode)
);

CREATE TABLE gobi_score(
	ccode TEXT,
	score INTEGER,
	license INTEGER,
	mreadable INTEGER,
	downloadable INTEGER,
	uptodate INTEGER,
	pubavail INTEGER,
	free INTEGER,
	PRIMARY KEY (ccode),
	FOREIGN KEY (ccode) REFERENCES country (ccode)
);

CREATE TABLE wb_series(
	scode TEXT,
	name TEXT,
	PRIMARY KEY (scode)
);

CREATE TABLE wb_series_data(
	scode TEXT,
	ccode TEXT,
	year INTEGER,
	svalue REAL,
	PRIMARY KEY (scode, ccode, year),
	FOREIGN KEY (scode) REFERENCES wb_series (scode),
	FOREIGN KEY (ccode) REFERENCES country (ccode)
);