-- IMPORTANT!!
-- THESE SQL QUERIES ARE NOT USED WHEN LOADING DEMO DATA
-- THESE ARE HERE TO ILLUSTRATE THE SQL EQUIVLENT OF THE SQLMODELS THAT ARE BEING USED TO CREATE THE DB

DROP TABLE IF EXISTS appointment;
DROP TABLE IF EXISTS patient;

CREATE TABLE patient (
    patient_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone TEXT
);

CREATE TABLE appointment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id INTEGER,
    appointment_date DATETIME,
    appointment_type TEXT NOT NULL,
    patient_id INTEGER,
    FOREIGN KEY (patient_id) REFERENCES patient (patient_id)
);