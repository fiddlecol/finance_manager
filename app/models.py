from app import db
from datetime import datetime
import enum
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)

class EventType(enum.Enum):
    BURIAL = "burial"
    WEDDING = "wedding"
    COMMUNITY = "community"
    MEDICAL = "medical"
    EDUCATION = "education"
    OTHER = "other"

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    event_type = db.Column(db.Enum(EventType), nullable=False, default=EventType.COMMUNITY)
    organizer_name = db.Column(db.String(100), nullable=False)
    organizer_phone = db.Column(db.String(20), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    event_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, closed, completed
    
    contributions = db.relationship('Contribution', backref='event', lazy=True, cascade='all, delete-orphan')
    admin = db.relationship('User', backref='events')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'event_type': self.event_type.value,
            'organizer_name': self.organizer_name,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'progress_percent': (self.current_amount / self.target_amount * 100) if self.target_amount > 0 else 0,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'created_at': self.created_at.isoformat(),
            'status': self.status,
            'contribution_count': len(self.contributions)
        }

class Contribution(db.Model):
    __tablename__ = 'contributions'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    contributor_name = db.Column(db.String(100), nullable=False)
    contributor_phone = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), default='mpesa')  # mpesa, bank, cash
    transaction_id = db.Column(db.String(100), unique=True, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'contributor_name': self.contributor_name,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class PaymentCallback(db.Model):
    __tablename__ = 'payment_callbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    contribution_id = db.Column(db.Integer, db.ForeignKey('contributions.id'), nullable=True)
    transaction_id = db.Column(db.String(100))
    mpesa_receipt_number = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    amount = db.Column(db.Float)
    status = db.Column(db.String(50))
    raw_response = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ExpenditureCategory(enum.Enum):
    SUPPLIES = "supplies"
    LABOR = "labor"
    TRANSPORT = "transport"
    VENUE = "venue"
    CATERING = "catering"
    MEDICINE = "medicine"
    UTILITIES = "utilities"
    OTHER = "other"

class Expenditure(db.Model):
    __tablename__ = 'expenditures'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.Enum(ExpenditureCategory), nullable=False, default=ExpenditureCategory.OTHER)
    approved_by = db.Column(db.String(100))  # Name of person approving
    receipt_url = db.Column(db.String(500))  # Optional: URL to receipt/proof
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    event = db.relationship('Event', backref='expenditures')
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'description': self.description,
            'amount': self.amount,
            'category': self.category.value,
            'approved_by': self.approved_by,
            'created_at': self.created_at.isoformat()
        }
