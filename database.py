"""
Design Diagnosis Database Module

SQLite database for storing:
- Form submissions
- Email verifications
- Payments
- Reports
- Report deliveries
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from dataclasses import dataclass
import json
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class FormSubmission:
    id: int
    email: str
    property_name: str
    airbnb_url: Optional[str]
    listing_type: str
    bedrooms: int
    bathrooms: int
    guest_capacity: int
    total_photos: str
    guest_comfort_checklist: List[str]
    report_type: str
    created_at: str


@dataclass
class EmailVerification:
    id: int
    submission_id: int
    email: str
    token: str
    verified: bool
    created_at: str
    expires_at: str


@dataclass
class Payment:
    id: int
    submission_id: int
    stripe_intent_id: str
    amount: int
    status: str
    created_at: str


@dataclass
class Report:
    id: int
    submission_id: int
    property_name: str
    vitality_score: float
    grade: str
    file_name: str
    report_type: str
    html_content: Optional[str] = None  # New: store HTML report
    created_at: str = ""


@dataclass
class ReportDelivery:
    id: int
    report_id: int
    email: str
    status: str
    created_at: str


# ============================================================================
# DATABASE CLASS
# ============================================================================

class DesignDiagnosisDB:
    """SQLite database for Design Diagnosis app"""
    
    def __init__(self, db_path: str = "design_diagnosis.db"):
        self.db_path = db_path
        self.conn = None
        self.init_db()
    
    def get_connection(self):
        """Get or create database connection"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Form Submissions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS form_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                property_name TEXT NOT NULL,
                airbnb_url TEXT,
                listing_type TEXT NOT NULL,
                bedrooms INTEGER NOT NULL,
                bathrooms INTEGER NOT NULL,
                guest_capacity INTEGER NOT NULL,
                total_photos TEXT NOT NULL,
                guest_comfort_checklist TEXT NOT NULL,
                report_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Email Verifications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id INTEGER NOT NULL,
                email TEXT NOT NULL,
                token TEXT NOT NULL UNIQUE,
                verified BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (submission_id) REFERENCES form_submissions(id)
            )
        """)
        
        # Payments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id INTEGER NOT NULL,
                stripe_intent_id TEXT NOT NULL UNIQUE,
                amount INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (submission_id) REFERENCES form_submissions(id)
            )
        """)
        
        # Reports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id INTEGER NOT NULL,
                property_name TEXT NOT NULL,
                vitality_score REAL NOT NULL,
                grade TEXT NOT NULL,
                file_name TEXT NOT NULL,
                report_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (submission_id) REFERENCES form_submissions(id)
            )
        """)
        
        # Report Deliveries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS report_deliveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER NOT NULL,
                email TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES reports(id)
            )
        """)
        
        conn.commit()
        logger.info(f"✅ Database initialized: {self.db_path}")
    
    # ========================================================================
    # FORM SUBMISSION OPERATIONS
    # ========================================================================
    
    def create_form_submission(
        self,
        email: str,
        property_name: str,
        listing_type: str,
        bedrooms: int,
        bathrooms: int,
        guest_capacity: int,
        total_photos: str,
        guest_comfort_checklist: List[str],
        report_type: str,
        airbnb_url: Optional[str] = None
    ) -> FormSubmission:
        """Create a new form submission"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        checklist_json = json.dumps(guest_comfort_checklist)
        
        cursor.execute("""
            INSERT INTO form_submissions
            (email, property_name, airbnb_url, listing_type, bedrooms, bathrooms,
             guest_capacity, total_photos, guest_comfort_checklist, report_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            email, property_name, airbnb_url, listing_type, bedrooms, bathrooms,
            guest_capacity, total_photos, checklist_json, report_type
        ))
        conn.commit()
        
        submission_id = cursor.lastrowid
        return self.get_form_submission(submission_id)
    
    def get_form_submission(self, submission_id: int) -> Optional[FormSubmission]:
        """Get form submission by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM form_submissions WHERE id = ?", (submission_id,))
        row = cursor.fetchone()
        
        if row:
            return FormSubmission(
                id=row[0],
                email=row[1],
                property_name=row[2],
                airbnb_url=row[3],
                listing_type=row[4],
                bedrooms=row[5],
                bathrooms=row[6],
                guest_capacity=row[7],
                total_photos=row[8],
                guest_comfort_checklist=json.loads(row[9]),
                report_type=row[10],
                created_at=row[11]
            )
        return None
    
    # ========================================================================
    # EMAIL VERIFICATION OPERATIONS
    # ========================================================================
    
    def create_email_verification(
        self,
        submission_id: int,
        email: str,
        token: str,
        expiry_hours: int = 24
    ) -> EmailVerification:
        """Create email verification token"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)
        
        cursor.execute("""
            INSERT INTO email_verifications
            (submission_id, email, token, expires_at)
            VALUES (?, ?, ?, ?)
        """, (submission_id, email, token, expires_at.isoformat()))
        conn.commit()
        
        return self.get_email_verification_by_token(token)
    
    def get_email_verification_by_token(self, token: str) -> Optional[EmailVerification]:
        """Get email verification by token"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM email_verifications WHERE token = ?", (token,))
        row = cursor.fetchone()
        
        if row:
            # Check if expired
            expires_at = datetime.fromisoformat(row[6])
            if datetime.utcnow() > expires_at:
                return None
            
            return EmailVerification(
                id=row[0],
                submission_id=row[1],
                email=row[2],
                token=row[3],
                verified=bool(row[4]),
                created_at=row[5],
                expires_at=row[6]
            )
        return None
    
    def mark_email_verified(self, verification_id: int):
        """Mark email as verified"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE email_verifications SET verified = 1 WHERE id = ?",
            (verification_id,)
        )
        conn.commit()
    
    # ========================================================================
    # PAYMENT OPERATIONS
    # ========================================================================
    
    def create_payment(
        self,
        submission_id: int,
        stripe_intent_id: str,
        amount: int,
        status: str = "pending"
    ) -> Payment:
        """Create payment record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO payments
            (submission_id, stripe_intent_id, amount, status)
            VALUES (?, ?, ?, ?)
        """, (submission_id, stripe_intent_id, amount, status))
        conn.commit()
        
        payment_id = cursor.lastrowid
        return self.get_payment(payment_id)
    
    def get_payment(self, payment_id: int) -> Optional[Payment]:
        """Get payment by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM payments WHERE id = ?", (payment_id,))
        row = cursor.fetchone()
        
        if row:
            return Payment(
                id=row[0],
                submission_id=row[1],
                stripe_intent_id=row[2],
                amount=row[3],
                status=row[4],
                created_at=row[5]
            )
        return None
    
    def get_payment_by_stripe_id(self, stripe_intent_id: str) -> Optional[Payment]:
        """Get payment by Stripe intent ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM payments WHERE stripe_intent_id = ?",
            (stripe_intent_id,)
        )
        row = cursor.fetchone()
        
        if row:
            return Payment(
                id=row[0],
                submission_id=row[1],
                stripe_intent_id=row[2],
                amount=row[3],
                status=row[4],
                created_at=row[5]
            )
        return None
    
    def update_payment_status(self, payment_id: int, status: str):
        """Update payment status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE payments SET status = ? WHERE id = ?",
            (status, payment_id)
        )
        conn.commit()
    
    # ========================================================================
    # REPORT OPERATIONS
    # ========================================================================
    
    def create_report(
        self,
        submission_id: int,
        vitality_score: float = 0,
        grade: str = "F",
        html_content: Optional[str] = None,
        report_type: str = "free",
        property_name: Optional[str] = None,
        file_name: Optional[str] = None
    ) -> Report:
        """Create report record (flexible parameters for backwards compatibility)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Ensure table has html_content column
        try:
            cursor.execute("""
                ALTER TABLE reports ADD COLUMN html_content TEXT
            """)
            conn.commit()
        except:
            pass  # Column likely already exists
        
        cursor.execute("""
            INSERT INTO reports
            (submission_id, property_name, vitality_score, grade, file_name, report_type, html_content)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (submission_id, property_name or "", vitality_score, grade, file_name or "", report_type, html_content))
        conn.commit()
        
        report_id = cursor.lastrowid
        return self.get_report(report_id)
    
    def get_report(self, report_id: int) -> Optional[Report]:
        """Get report by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
        row = cursor.fetchone()
        
        if row:
            return Report(
                id=row[0],
                submission_id=row[1],
                property_name=row[2],
                vitality_score=row[3],
                grade=row[4],
                file_name=row[5],
                report_type=row[6],
                created_at=row[7]
            )
        return None
    
    # ========================================================================
    # REPORT DELIVERY OPERATIONS
    # ========================================================================
    
    def create_report_delivery(
        self,
        report_id: int,
        email: str,
        status: str = "pending"
    ) -> ReportDelivery:
        """Create report delivery record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO report_deliveries
            (report_id, email, status)
            VALUES (?, ?, ?)
        """, (report_id, email, status))
        conn.commit()
        
        delivery_id = cursor.lastrowid
        return self.get_report_delivery(delivery_id)
    
    def get_report_delivery(self, delivery_id: int) -> Optional[ReportDelivery]:
        """Get report delivery by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM report_deliveries WHERE id = ?", (delivery_id,))
        row = cursor.fetchone()
        
        if row:
            return ReportDelivery(
                id=row[0],
                report_id=row[1],
                email=row[2],
                status=row[3],
                created_at=row[4]
            )
        return None
    
    # ========================================================================
    # UTILITY OPERATIONS
    # ========================================================================
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("✅ Database connection closed")
    
    def reset_db(self):
        """Reset all tables (for testing)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DROP TABLE IF EXISTS report_deliveries")
        cursor.execute("DROP TABLE IF EXISTS reports")
        cursor.execute("DROP TABLE IF EXISTS payments")
        cursor.execute("DROP TABLE IF EXISTS email_verifications")
        cursor.execute("DROP TABLE IF EXISTS form_submissions")
        
        conn.commit()
        logger.info("✅ Database reset")
        
        self.init_db()


# Singleton instance
_db_instance: Optional[DesignDiagnosisDB] = None


def get_db(db_path: str = "design_diagnosis.db") -> DesignDiagnosisDB:
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DesignDiagnosisDB(db_path)
    return _db_instance
