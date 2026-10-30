import unittest
import sqlite3
import os

class TestLocalSQLitePersistence(unittest.TestCase):
    def setUp(self):
        self.db_path = "backend/tests/test_local.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def tearDown(self):
        self.conn.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_schema_creation_and_queries(self):
        # Create standard tables matching SQLCipher local schema
        self.cursor.executescript("""
        CREATE TABLE patients (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            target_glucose_min INTEGER DEFAULT 70,
            target_glucose_max INTEGER DEFAULT 130
        );

        CREATE TABLE biometric_records (
            id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            metric_type TEXT NOT NULL,
            value_primary REAL NOT NULL,
            value_secondary REAL,
            context TEXT NOT NULL,
            is_alert INTEGER DEFAULT 0,
            timestamp TEXT NOT NULL
        );

        CREATE TABLE medications (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            dose_mg REAL NOT NULL,
            scheduled_time TEXT NOT NULL
        );

        CREATE TABLE adherence_records (
            id TEXT PRIMARY KEY,
            medication_id TEXT NOT NULL,
            taken_time TEXT NOT NULL,
            status TEXT NOT NULL
        );
        """)

        # Insert test patient
        self.cursor.execute("INSERT INTO patients VALUES ('p1', 'Ramón', 58, 70, 130)")
        
        # Insert biometrics
        self.cursor.execute("INSERT INTO biometric_records VALUES ('b1', 'p1', 'GLUCOSE', 114.0, NULL, 'FASTING', 0, '2026-10-30T08:30:00Z')")
        self.cursor.execute("INSERT INTO biometric_records VALUES ('b2', 'p1', 'BLOOD_PRESSURE', 124.0, 82.0, 'FASTING', 0, '2026-10-30T08:35:00Z')")
        
        # Insert medication & adherence
        self.cursor.execute("INSERT INTO medications VALUES ('m1', 'Metformina 850mg', 850, '08:30')")
        self.cursor.execute("INSERT INTO adherence_records VALUES ('a1', 'm1', '2026-10-30T08:32:00Z', 'TAKEN_ON_TIME')")
        self.conn.commit()

        # Query and assert
        self.cursor.execute("SELECT AVG(value_primary) FROM biometric_records WHERE metric_type = 'GLUCOSE'")
        avg_glucose = self.cursor.fetchone()[0]
        self.assertEqual(avg_glucose, 114.0)

        self.cursor.execute("SELECT COUNT(*) FROM adherence_records WHERE status = 'TAKEN_ON_TIME'")
        adherence_count = self.cursor.fetchone()[0]
        self.assertEqual(adherence_count, 1)

if __name__ == '__main__':
    unittest.main()
