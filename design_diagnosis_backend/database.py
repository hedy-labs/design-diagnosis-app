"""
Design Diagnosis Backend — SQLite Database Schema & ORM

Database tracks properties, reports, and scoring across 7 dimensions.
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict
import json

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Property:
    """Represents an Airbnb property being analyzed"""
    id: Optional[int] = None
    airbnb_url: str = ""
    airbnb_id: str = ""
    property_name: str = ""
    location: str = ""
    bedrooms: int = 0
    bathrooms: int = 0
    guest_capacity: int = 0
    created_at: str = ""
    updated_at: str = ""


@dataclass
class DimensionScore:
    """Individual dimension score (1–7)"""
    id: Optional[int] = None
    report_id: int = 0
    dimension: int = 1  # 1–7
    score: float = 0.0  # 0–20, 0–10, or 0–20 depending on dimension
    max_points: float = 20.0
    notes: str = ""
    created_at: str = ""


@dataclass
class Report:
    """Complete Vitality Score report for a property"""
    id: Optional[int] = None
    property_id: int = 0
    vitality_score: float = 0.0  # 0–100 (final scaled score)
    grade: str = "F"  # A, B, C, D, F
    total_points: float = 0.0  # sum of all dimensions (0–150)
    
    # Individual dimension scores (stored separately)
    dimension_scores: Dict[int, float] = None  # {1: 18.5, 2: 15, ...}
    
    # Photo data
    photo_count: int = 0
    photo_score: float = 0.0
    photo_notes: str = ""
    
    # Hidden friction data
    hidden_friction_score: float = 0.0
    hidden_friction_items_missing: List[str] = None
    hidden_friction_cost_estimate: float = 0.0
    
    # Metadata
    created_at: str = ""
    updated_at: str = ""
    report_pdf_path: Optional[str] = None


@dataclass
class HiddenFrictionItem:
    """Individual item from the 42-item Hidden Friction checklist"""
    id: Optional[int] = None
    report_id: int = 0
    category: str = ""  # BEDROOM, BATHROOM, KITCHEN, LAUNDRY, LIVING, MAINTENANCE
    item_name: str = ""
    quantity_required: int = 1
    quantity_present: int = 0
    severity: str = "medium"  # critical, high, medium, low
    point_deduction: float = 0.0
    notes: str = ""


@dataclass
class FormSubmission:
    """Form submission with property data and guest comfort checklist"""
    id: Optional[int] = None
    email: str = ""
    property_name: str = ""
    airbnb_url: str = ""
    listing_type: str = ""  # House, Condo, Apartment, Studio, Suite, Private Room
    bedrooms: int = 0
    bathrooms: int = 0
    guest_capacity: int = 0
    total_photos: str = ""  # JSON or string like "11-15"
    guest_comfort_checklist: str = ""  # JSON of checked items
    report_type: str = "free"  # "free" or "premium"
    ip_address: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass
class EmailVerification:
    """Email verification token and status"""
    id: Optional[int] = None
    submission_id: int = 0
    email: str = ""
    token: str = ""
    verified: bool = False
    verified_at: Optional[str] = None
    token_expiry: str = ""
    created_at: str = ""


@dataclass
class Payment:
    """Stripe payment record"""
    id: Optional[int] = None
    submission_id: int = 0
    stripe_payment_intent_id: str = ""
    amount: int = 0  # in cents
    currency: str = "usd"
    status: str = ""  # pending, succeeded, failed
    report_type: str = "premium"
    webhook_received: bool = False
    created_at: str = ""
    updated_at: str = ""


@dataclass
class ReportDelivery:
    """Delivery tracking for sent reports"""
    id: Optional[int] = None
    submission_id: int = 0
    email: str = ""
    report_type: str = ""
    pdf_path: str = ""
    sent_at: Optional[str] = None
    email_status: str = ""  # pending, sent, bounced, failed
    created_at: str = ""


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

class DesignDiagnosisDB:
    """SQLite database for Design Diagnosis backend"""
    
    def __init__(self, db_path: str = "design_diagnosis.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Create database schema if not exists"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Properties table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS properties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    airbnb_url TEXT UNIQUE,
                    airbnb_id TEXT UNIQUE,
                    property_name TEXT NOT NULL,
                    location TEXT,
                    bedrooms INTEGER DEFAULT 0,
                    bathrooms INTEGER DEFAULT 0,
                    guest_capacity INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Reports table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    property_id INTEGER NOT NULL UNIQUE,
                    vitality_score REAL DEFAULT 0.0,
                    grade TEXT DEFAULT 'F',
                    total_points REAL DEFAULT 0.0,
                    dimension_scores_json TEXT,
                    
                    photo_count INTEGER DEFAULT 0,
                    photo_score REAL DEFAULT 0.0,
                    photo_notes TEXT,
                    
                    hidden_friction_score REAL DEFAULT 0.0,
                    hidden_friction_missing_json TEXT,
                    hidden_friction_cost_estimate REAL DEFAULT 0.0,
                    
                    report_pdf_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (property_id) REFERENCES properties(id)
                )
            """)
            
            # Dimension scores table (detailed breakdown)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dimension_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id INTEGER NOT NULL,
                    dimension INTEGER NOT NULL,
                    score REAL NOT NULL,
                    max_points REAL NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (report_id) REFERENCES reports(id)
                )
            """)
            
            # Hidden friction items (42-item checklist breakdown)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hidden_friction_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id INTEGER NOT NULL,
                    category TEXT,
                    item_name TEXT,
                    quantity_required INTEGER DEFAULT 1,
                    quantity_present INTEGER DEFAULT 0,
                    severity TEXT,
                    point_deduction REAL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (report_id) REFERENCES reports(id)
                )
            """)
            
            # Form submissions (captures guest comfort checklist + property data)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS form_submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    property_name TEXT,
                    airbnb_url TEXT,
                    listing_type TEXT,
                    bedrooms INTEGER,
                    bathrooms INTEGER,
                    guest_capacity INTEGER,
                    total_photos TEXT,
                    guest_comfort_checklist TEXT,
                    report_type TEXT NOT NULL,
                    ip_address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Email verification tokens
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_verifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    submission_id INTEGER NOT NULL,
                    email TEXT NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    verified BOOLEAN DEFAULT 0,
                    verified_at TIMESTAMP,
                    token_expiry TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (submission_id) REFERENCES form_submissions(id)
                )
            """)
            
            # Stripe payments
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    submission_id INTEGER NOT NULL,
                    stripe_payment_intent_id TEXT UNIQUE,
                    amount INTEGER,
                    currency TEXT DEFAULT 'usd',
                    status TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    webhook_received BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (submission_id) REFERENCES form_submissions(id)
                )
            """)
            
            # Report delivery tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS report_deliveries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    submission_id INTEGER NOT NULL,
                    email TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    pdf_path TEXT,
                    sent_at TIMESTAMP,
                    email_status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (submission_id) REFERENCES form_submissions(id)
                )
            """)
            
            conn.commit()
    
    # ========================================================================
    # PROPERTIES CRUD
    # ========================================================================
    
    def create_property(self, property: Property) -> int:
        """Create new property, return ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO properties (airbnb_url, airbnb_id, property_name, location, bedrooms, bathrooms, guest_capacity)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                property.airbnb_url,
                property.airbnb_id,
                property.property_name,
                property.location,
                property.bedrooms,
                property.bathrooms,
                property.guest_capacity
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_property(self, property_id: int) -> Optional[Property]:
        """Retrieve property by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM properties WHERE id = ?", (property_id,))
            row = cursor.fetchone()
            if row:
                return Property(
                    id=row[0], airbnb_url=row[1], airbnb_id=row[2],
                    property_name=row[3], location=row[4], bedrooms=row[5],
                    bathrooms=row[6], guest_capacity=row[7],
                    created_at=row[8], updated_at=row[9]
                )
        return None
    
    # ========================================================================
    # REPORTS CRUD
    # ========================================================================
    
    def create_report(self, property_id: int) -> int:
        """Create new report for property, return report ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO reports (property_id)
                VALUES (?)
            """, (property_id,))
            conn.commit()
            return cursor.lastrowid
    
    def get_report(self, report_id: int) -> Optional[Report]:
        """Retrieve report with all dimension scores"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
            row = cursor.fetchone()
            if not row:
                return None
            
            report = Report(
                id=row[0], property_id=row[1], vitality_score=row[2],
                grade=row[3], total_points=row[4],
                dimension_scores=json.loads(row[5] or "{}"),
                photo_count=row[6], photo_score=row[7], photo_notes=row[8],
                hidden_friction_score=row[9],
                hidden_friction_items_missing=json.loads(row[10] or "[]"),
                hidden_friction_cost_estimate=row[11],
                report_pdf_path=row[12],
                created_at=row[13], updated_at=row[14]
            )
            return report
    
    def update_report_scores(
        self, report_id: int, vitality_score: float, grade: str, total_points: float,
        dimension_scores: Dict[int, float]
    ):
        """Update report with calculated scores"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE reports 
                SET vitality_score = ?, grade = ?, total_points = ?, dimension_scores_json = ?
                WHERE id = ?
            """, (
                vitality_score, grade, total_points,
                json.dumps(dimension_scores),
                report_id
            ))
            conn.commit()
    
    def update_report_photo_score(self, report_id: int, photo_count: int, photo_score: float, notes: str = ""):
        """Update report with photo strategy score"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE reports 
                SET photo_count = ?, photo_score = ?, photo_notes = ?
                WHERE id = ?
            """, (photo_count, photo_score, notes, report_id))
            conn.commit()
    
    def update_report_hidden_friction(
        self, report_id: int, score: float, missing_items: List[str], cost_estimate: float
    ):
        """Update report with hidden friction score"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE reports 
                SET hidden_friction_score = ?, hidden_friction_missing_json = ?, hidden_friction_cost_estimate = ?
                WHERE id = ?
            """, (score, json.dumps(missing_items), cost_estimate, report_id))
            conn.commit()
    
    # ========================================================================
    # DIMENSION SCORES
    # ========================================================================
    
    def save_dimension_score(self, report_id: int, dimension: int, score: float, max_points: float, notes: str = ""):
        """Save individual dimension score"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO dimension_scores (report_id, dimension, score, max_points, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (report_id, dimension, score, max_points, notes))
            conn.commit()
    
    def get_dimension_scores(self, report_id: int) -> List[DimensionScore]:
        """Get all dimension scores for a report"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM dimension_scores WHERE report_id = ? ORDER BY dimension
            """, (report_id,))
            rows = cursor.fetchall()
            return [
                DimensionScore(
                    id=row[0], report_id=row[1], dimension=row[2],
                    score=row[3], max_points=row[4], notes=row[5], created_at=row[6]
                )
                for row in rows
            ]
    
    # ========================================================================
    # HIDDEN FRICTION ITEMS
    # ========================================================================
    
    def save_hidden_friction_item(
        self, report_id: int, category: str, item_name: str,
        quantity_required: int, quantity_present: int,
        severity: str, point_deduction: float, notes: str = ""
    ):
        """Save individual hidden friction item"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO hidden_friction_items 
                (report_id, category, item_name, quantity_required, quantity_present, severity, point_deduction, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (report_id, category, item_name, quantity_required, quantity_present, severity, point_deduction, notes))
            conn.commit()
    
    def get_hidden_friction_items(self, report_id: int) -> List[HiddenFrictionItem]:
        """Get all hidden friction items for a report"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM hidden_friction_items WHERE report_id = ?
            """, (report_id,))
            rows = cursor.fetchall()
            return [
                HiddenFrictionItem(
                    id=row[0], report_id=row[1], category=row[2],
                    item_name=row[3], quantity_required=row[4],
                    quantity_present=row[5], severity=row[6],
                    point_deduction=row[7], notes=row[8]
                )
                for row in rows
            ]
    
    # ========================================================================
    # PHASE 2: FORM SUBMISSIONS
    # ========================================================================
    
    def create_form_submission(self, submission: FormSubmission) -> int:
        """Create new form submission, return ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO form_submissions 
                (email, property_name, airbnb_url, listing_type, bedrooms, bathrooms, 
                 guest_capacity, total_photos, guest_comfort_checklist, report_type, ip_address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                submission.email, submission.property_name, submission.airbnb_url,
                submission.listing_type, submission.bedrooms, submission.bathrooms,
                submission.guest_capacity, submission.total_photos,
                submission.guest_comfort_checklist, submission.report_type,
                submission.ip_address
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_form_submission(self, submission_id: int) -> Optional[FormSubmission]:
        """Get form submission by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM form_submissions WHERE id = ?", (submission_id,))
            row = cursor.fetchone()
            if row:
                return FormSubmission(
                    id=row[0], email=row[1], property_name=row[2], airbnb_url=row[3],
                    listing_type=row[4], bedrooms=row[5], bathrooms=row[6],
                    guest_capacity=row[7], total_photos=row[8],
                    guest_comfort_checklist=row[9], report_type=row[10],
                    ip_address=row[11], created_at=row[12], updated_at=row[13]
                )
        return None
    
    # ========================================================================
    # EMAIL VERIFICATION
    # ========================================================================
    
    def create_email_verification(
        self, submission_id: int, email: str, token: str, token_expiry: str
    ) -> int:
        """Create email verification token"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO email_verifications (submission_id, email, token, token_expiry)
                VALUES (?, ?, ?, ?)
            """, (submission_id, email, token, token_expiry))
            conn.commit()
            return cursor.lastrowid
    
    def get_email_verification_by_token(self, token: str) -> Optional[EmailVerification]:
        """Get verification by token"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email_verifications WHERE token = ?", (token,))
            row = cursor.fetchone()
            if row:
                return EmailVerification(
                    id=row[0], submission_id=row[1], email=row[2], token=row[3],
                    verified=bool(row[4]), verified_at=row[5], token_expiry=row[6],
                    created_at=row[7]
                )
        return None
    
    def mark_email_verified(self, token: str) -> bool:
        """Mark email as verified"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE email_verifications 
                SET verified = 1, verified_at = CURRENT_TIMESTAMP
                WHERE token = ?
            """, (token,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_email_verification_by_submission(self, submission_id: int) -> Optional[EmailVerification]:
        """Get verification for a submission"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM email_verifications WHERE submission_id = ?
            """, (submission_id,))
            row = cursor.fetchone()
            if row:
                return EmailVerification(
                    id=row[0], submission_id=row[1], email=row[2], token=row[3],
                    verified=bool(row[4]), verified_at=row[5], token_expiry=row[6],
                    created_at=row[7]
                )
        return None
    
    # ========================================================================
    # PAYMENTS
    # ========================================================================
    
    def create_payment(
        self, submission_id: int, stripe_payment_intent_id: str,
        amount: int, status: str, report_type: str
    ) -> int:
        """Create payment record"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO payments 
                (submission_id, stripe_payment_intent_id, amount, status, report_type)
                VALUES (?, ?, ?, ?, ?)
            """, (submission_id, stripe_payment_intent_id, amount, status, report_type))
            conn.commit()
            return cursor.lastrowid
    
    def get_payment_by_intent(self, stripe_payment_intent_id: str) -> Optional[Payment]:
        """Get payment by Stripe intent ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM payments WHERE stripe_payment_intent_id = ?
            """, (stripe_payment_intent_id,))
            row = cursor.fetchone()
            if row:
                return Payment(
                    id=row[0], submission_id=row[1],
                    stripe_payment_intent_id=row[2], amount=row[3], currency=row[4],
                    status=row[5], report_type=row[6], webhook_received=bool(row[7]),
                    created_at=row[8], updated_at=row[9]
                )
        return None
    
    def update_payment_status(self, payment_id: int, status: str) -> bool:
        """Update payment status"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE payments 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, payment_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def mark_webhook_received(self, payment_id: int) -> bool:
        """Mark that webhook was received for payment"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE payments 
                SET webhook_received = 1
                WHERE id = ?
            """, (payment_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # ========================================================================
    # REPORT DELIVERY
    # ========================================================================
    
    def create_report_delivery(
        self, submission_id: int, email: str, report_type: str, pdf_path: str
    ) -> int:
        """Create report delivery record"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO report_deliveries (submission_id, email, report_type, pdf_path)
                VALUES (?, ?, ?, ?)
            """, (submission_id, email, report_type, pdf_path))
            conn.commit()
            return cursor.lastrowid
    
    def mark_delivery_sent(self, delivery_id: int, email_status: str = "sent") -> bool:
        """Mark report as sent"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE report_deliveries 
                SET sent_at = CURRENT_TIMESTAMP, email_status = ?
                WHERE id = ?
            """, (email_status, delivery_id))
            conn.commit()
            return cursor.rowcount > 0


# Test initialization
if __name__ == "__main__":
    db = DesignDiagnosisDB("design_diagnosis.db")
    print("✅ Database initialized successfully")
