from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os

from models import db, Bank, User, LoanType, KycRequirement, Application, KycDocumentUpload

app = Flask(__name__)
app.secret_key = "your-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///loan_kyc.db"  # Use PostgreSQL on Render
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db.init_app(app)

# ------------------------
# Admin Login & Logout
# ------------------------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = user.role
            session['bank_id'] = user.bank_id
            flash("Login successful.")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid credentials.")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for("admin_login"))

# ------------------------
# Admin Dashboard (placeholder)
# ------------------------
@app.route("/admin/dashboard")
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for("admin_login"))

    user = User.query.get(session['user_id'])
    bank = Bank.query.get(user.bank_id) if user.bank_id else None
    return render_template("admin_dashboard.html", user=user, bank=bank)

# ------------------------
# Loan Application
# ------------------------
@app.route("/bank/<int:bank_id>/apply", methods=["GET", "POST"])
def submit_loan_application(bank_id):
    bank = Bank.query.get_or_404(bank_id)
    loan_types = LoanType.query.filter_by(bank_id=bank.id).all()

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        has_account = request.form.get("has_account")
        account_number = request.form.get("account_number") if has_account == 'yes' else None
        loan_type_id = int(request.form.get("loan_type_id"))
        amount_requested = float(request.form.get("amount_requested"))

        application = Application(
            bank_id=bank_id,
            loan_type_id=loan_type_id,
            applicant_name=name,
            email=email,
            phone=phone,
            account_number=account_number,
            amount_requested=amount_requested
        )
        db.session.add(application)
        db.session.commit()

        loan = LoanType.query.get(loan_type_id)
        for idx, kyc in enumerate(loan.kyc_requirements):
            doc_field = f"kyc_{loan_type_id}_{idx + 1}"
            if doc_field in request.files:
                file = request.files[doc_field]
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)

                    doc_upload = KycDocumentUpload(
                        application_id=application.id,
                        document_name=kyc.document_name,
                        file_path=filepath
                    )
                    db.session.add(doc_upload)

        db.session.commit()
        flash("Loan application submitted successfully.")
        return redirect(url_for("submit_loan_application", bank_id=bank_id))

    return render_template("loan_form.html", bank=bank, loan_types=loan_types)

# ------------------------
# Home Page (optional)
# ------------------------
@app.route("/")
def home():
    return "Welcome to the Loan & KYC App. Please choose a bank or login as Admin."

# ------------------------
# CLI for DB Init
# ------------------------
@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("Database initialized.")

            
                    
