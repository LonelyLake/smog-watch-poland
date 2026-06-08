CREATE TABLE IF NOT EXISTS measurements (
	timestamp TIMESTAMPTZ NOT NULL,
	value FLOAT NOT NULL,
	parameter VARCHAR(50) NOT NULL,
	station VARCHAR(50) NOT NULL,
	PRIMARY KEY (timestamp, parameter, station)
);