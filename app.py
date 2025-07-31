import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from models import db, Bank, LoanType, KycRequirement, Application, KycDocumentUpload

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///loan_kyc.db'
db.init_app(app)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
