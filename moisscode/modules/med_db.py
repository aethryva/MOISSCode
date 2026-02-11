"""
med.db  - Database Layer for MOISSCode
Provides persistent storage for patients, protocol results, and audit trails.
Uses SQLite for zero-config local storage. Production systems can swap to PostgreSQL.
"""

import sqlite3
import json
import datetime
import os
from typing import Dict, List, Any, Optional


class MedDatabase:
    """Protocol-aware medical database."""

    def __init__(self, db_path: str = "moisscode_data.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self):
        """Create tables if they don't exist."""
        cursor = self.conn.cursor()

        # Patients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT UNIQUE NOT NULL,
                name TEXT,
                age INTEGER,
                weight REAL,
                sex TEXT,
                vitals TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Protocol runs (audit trail)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS protocol_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                protocol_name TEXT NOT NULL,
                patient_id TEXT,
                status TEXT DEFAULT 'RUNNING',
                events TEXT,
                started_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT,
                run_by TEXT DEFAULT 'system'
            )
        """)

        # Interventions log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interventions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                protocol_run_id INTEGER,
                drug_name TEXT,
                dose TEXT,
                moiss_class TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (protocol_run_id) REFERENCES protocol_runs(id)
            )
        """)

        # Lab results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lab_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                test_name TEXT NOT NULL,
                value REAL,
                unit TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                is_critical INTEGER DEFAULT 0
            )
        """)

        # Alerts history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                protocol_run_id INTEGER,
                message TEXT,
                severity TEXT,
                acknowledged INTEGER DEFAULT 0,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (protocol_run_id) REFERENCES protocol_runs(id)
            )
        """)

        # Billing ledger
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS billing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                protocol_run_id INTEGER,
                cpt_code TEXT,
                description TEXT,
                amount REAL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (protocol_run_id) REFERENCES protocol_runs(id)
            )
        """)

        self.conn.commit()

    # ─── Patient Operations ────────────────────────────────────
    def save_patient(self, patient_id: str, name: str = "", age: int = 0,
                     weight: float = 0.0, sex: str = "", vitals: Dict = None,
                     metadata: Dict = None) -> Dict:
        """Save or update a patient record."""
        cursor = self.conn.cursor()
        vitals_json = json.dumps(vitals or {})
        meta_json = json.dumps(metadata or {})
        now = datetime.datetime.now().isoformat()

        try:
            cursor.execute("""
                INSERT INTO patients (patient_id, name, age, weight, sex, vitals, metadata, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(patient_id) DO UPDATE SET
                    name=excluded.name, age=excluded.age, weight=excluded.weight,
                    sex=excluded.sex, vitals=excluded.vitals, metadata=excluded.metadata,
                    updated_at=excluded.updated_at
            """, (patient_id, name, age, weight, sex, vitals_json, meta_json, now))
            self.conn.commit()
            print(f"[DB] Saved patient {patient_id}")
            return {"type": "DB_EVENT", "action": "SAVE_PATIENT", "patient_id": patient_id}
        except Exception as e:
            print(f"[DB] Error saving patient: {e}")
            return {"type": "DB_ERROR", "error": str(e)}

    def get_patient(self, patient_id: str) -> Optional[Dict]:
        """Retrieve a patient record."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
        row = cursor.fetchone()
        if row:
            result = dict(row)
            result['vitals'] = json.loads(result['vitals'])
            result['metadata'] = json.loads(result['metadata'])
            return result
        return None

    def list_patients(self, limit: int = 50) -> List[Dict]:
        """List all patients."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT patient_id, name, age, weight, updated_at FROM patients ORDER BY updated_at DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]

    # ─── Protocol Run (Audit Trail) ────────────────────────────
    def start_run(self, protocol_name: str, patient_id: str = None, run_by: str = "system") -> int:
        """Start a new protocol run, returns run ID."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO protocol_runs (protocol_name, patient_id, status, run_by)
            VALUES (?, ?, 'RUNNING', ?)
        """, (protocol_name, patient_id, run_by))
        self.conn.commit()
        run_id = cursor.lastrowid
        print(f"[DB] Protocol run {run_id} started: {protocol_name}")
        return run_id

    def end_run(self, run_id: int, events: List[Dict] = None, status: str = "COMPLETED"):
        """End a protocol run."""
        cursor = self.conn.cursor()
        now = datetime.datetime.now().isoformat()
        events_json = json.dumps(events or [])
        cursor.execute("""
            UPDATE protocol_runs SET status=?, events=?, completed_at=? WHERE id=?
        """, (status, events_json, now, run_id))
        self.conn.commit()
        print(f"[DB] Protocol run {run_id} ended: {status}")

    def get_run(self, run_id: int) -> Optional[Dict]:
        """Get a specific protocol run."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM protocol_runs WHERE id = ?", (run_id,))
        row = cursor.fetchone()
        if row:
            result = dict(row)
            result['events'] = json.loads(result['events']) if result['events'] else []
            return result
        return None

    def list_runs(self, patient_id: str = None, limit: int = 50) -> List[Dict]:
        """List protocol runs, optionally filtered by patient."""
        cursor = self.conn.cursor()
        if patient_id:
            cursor.execute("""
                SELECT id, protocol_name, patient_id, status, started_at, completed_at
                FROM protocol_runs WHERE patient_id = ?
                ORDER BY started_at DESC LIMIT ?
            """, (patient_id, limit))
        else:
            cursor.execute("""
                SELECT id, protocol_name, patient_id, status, started_at, completed_at
                FROM protocol_runs ORDER BY started_at DESC LIMIT ?
            """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

    # ─── Intervention Logging ──────────────────────────────────
    def log_intervention(self, run_id: int, drug_name: str, dose: str, moiss_class: str):
        """Log a drug intervention."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO interventions (protocol_run_id, drug_name, dose, moiss_class)
            VALUES (?, ?, ?, ?)
        """, (run_id, drug_name, dose, moiss_class))
        self.conn.commit()
        print(f"[DB] Logged intervention: {drug_name} ({dose}) [{moiss_class}]")

    # ─── Lab Results ───────────────────────────────────────────
    def save_lab(self, patient_id: str, test_name: str, value: float,
                 unit: str = "", is_critical: bool = False) -> Dict:
        """Save a lab result."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO lab_results (patient_id, test_name, value, unit, is_critical)
            VALUES (?, ?, ?, ?, ?)
        """, (patient_id, test_name, value, unit, int(is_critical)))
        self.conn.commit()
        print(f"[DB] Lab: {test_name} = {value} {unit} {'⚠️ CRITICAL' if is_critical else ''}")
        return {"type": "DB_EVENT", "action": "SAVE_LAB", "test": test_name, "value": value}

    def get_labs(self, patient_id: str, test_name: str = None, limit: int = 10) -> List[Dict]:
        """Get lab results for a patient, optionally filtered by test name."""
        cursor = self.conn.cursor()
        if test_name:
            cursor.execute("""
                SELECT * FROM lab_results WHERE patient_id = ? AND test_name = ?
                ORDER BY timestamp DESC LIMIT ?
            """, (patient_id, test_name, limit))
        else:
            cursor.execute("""
                SELECT * FROM lab_results WHERE patient_id = ?
                ORDER BY timestamp DESC LIMIT ?
            """, (patient_id, limit))
        return [dict(row) for row in cursor.fetchall()]

    # ─── Alert Logging ─────────────────────────────────────────
    def log_alert(self, run_id: int, message: str, severity: str = "info"):
        """Log an alert."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO alerts (protocol_run_id, message, severity)
            VALUES (?, ?, ?)
        """, (run_id, message, severity))
        self.conn.commit()

    # ─── Billing ───────────────────────────────────────────────
    def log_billing(self, run_id: int, cpt_code: str, description: str, amount: float):
        """Log a billing event."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO billing (protocol_run_id, cpt_code, description, amount)
            VALUES (?, ?, ?, ?)
        """, (run_id, cpt_code, description, amount))
        self.conn.commit()

    def get_billing_total(self, run_id: int = None) -> float:
        """Get total billing amount, optionally for a specific run."""
        cursor = self.conn.cursor()
        if run_id:
            cursor.execute("SELECT SUM(amount) as total FROM billing WHERE protocol_run_id = ?", (run_id,))
        else:
            cursor.execute("SELECT SUM(amount) as total FROM billing")
        row = cursor.fetchone()
        return row['total'] if row and row['total'] else 0.0

    # ─── Cleanup ───────────────────────────────────────────────
    def close(self):
        """Close the database connection."""
        self.conn.close()

    def __del__(self):
        try:
            self.conn.close()
        except:
            pass
