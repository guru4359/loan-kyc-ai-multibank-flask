# models.py

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Bank Info
class Bank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    logo = db.Column(db.String(255))
    address = db.Column(db.String(255))
    theme_color = db.Column(db.String(20))

    loan_types = db.relationship('LoanType', backref='bank', lazy=True)
    users = db.relationship('User', backref='bank', lazy=True)

# Admin / SuperAdmin Users
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='admin')  # 'admin' or 'superadmin'
    bank_id = db.Column(db.Integer, db.ForeignKey('bank.id'), nullable=True)  # SuperAdmin can have null

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Loan Types per Bank
class LoanType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bank_id = db.Column(db.Integer, db.ForeignKey('bank.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    min_amount = db.Column(db.Float)
    max_amount = db.Column(db.Float)
    interest_rate = db.Column(db.Float)
    term_months = db.Column(db.String(50))  # Comma-separated: "12,24,36"

    kyc_requirements = db.relationship('KycRequirement', backref='loan_type', lazy=True)

# KYC Requirement Config
class KycRequirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loan_type_id = db.Column(db.Integer, db.ForeignKey('loan_type.id'), nullable=False)
    document_name = db.Column(db.String(100), nullable=False)
    required = db.Column(db.Boolean, default=True)

# Loan Applications
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bank_id = db.Column(db.Integer, db.ForeignKey('bank.id'))
    loan_type_id = db.Column(db.Integer, db.ForeignKey('loan_type.id'))
    applicant_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    account_number = db.Column(db.String(50), nullable=True)
    amount_requested = db.Column(db.Float)
    status = db.Column(db.String(50), default='Submitted')  # 'Submitted', 'Under Review', etc.

    kyc_documents = db.relationship('KycDocumentUpload', backref='application', lazy=True)

# Uploaded KYC Documents
class KycDocumentUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'))
    document_name = db.Column(db.String(100))
    file_path = db.Column(db.String(255))

# Savings Account Request
class AccountRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bank_id = db.Column(db.Integer, db.ForeignKey('bank.id'))
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    submitted_at = db.Column(db.DateTime, server_default=db.func.now())
