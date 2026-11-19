# ----- Job Application Tracker - Flask application -----

import re
from datetime import date, datetime

import mysql.connector
from flask import Flask, abort, flash, redirect, render_template, request, url_for

import database as db

app = Flask(__name__)
app.secret_key = "job-tracker-secret-key"

JOB_TYPES = ["Full-time", "Part-time", "Contract", "Internship"]
STATUSES = ["Applied", "Screening", "Interview", "Offer", "Rejected", "Withdrawn"]
INTERVIEW_TYPES = ["Phone", "Video", "On-site", "Technical", "Panel", "Other"]

MAX_INT = 2147483647
CONNECTION_ERRORS = (1045, 1049, 2003, 2005)

EMAIL_RE =re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
URL_RE = re.compile(r"^https?://[^\s]+\.[^\s]+$", re.IGNORECASE)
PHONE_RE = re.compile(r"^[0-9+()\-.\s]{7,20}$")


# ----- Validation helpers -----

def clean(form, field):
    value = form.get(field, "").strip()
    return value or None


def check_length(value, max_len, label, errors):
    if value and len(value) > max_len:
        errors.append(f"{label} must be {max_len} characters or fewer.")


def check_url(value, label, errors):
    if value and not URL_RE.match(value):
        errors.append(f"{label} must be a valid URL starting with http:// or https://.")


def check_date(value, label, errors, required=False):
    if not value:
        if required:
            errors.append(f"{label} is required.")
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        errors.append(f"{label} must be a valid date (YYYY-MM-DD).")
        return None


def check_int(value, label, errors):
    if not value:
        return None
    try:
        number = int(value)
    except ValueError:
        errors.append(f"{label} must be a whole number.")
        return None
    if number < 0:
        errors.append(f"{label} cannot be negative.")
    elif number > MAX_INT:
        errors.append(f"{label} is too large (maximum {MAX_INT:,}).")
    return number


def parse_skills(text):
    skills = []
    seen = set()
    for part in (text or "").split(","):
        skill = part.strip()
        if skill and skill.lower() not in seen:
            seen.add(skill.lower())
            skills.append(skill)
    return skills


def validate_company(form):
    errors = []
    data = {f: clean(form, f) for f in
            ["company_name", "industry", "website", "city", "state", "notes"]}
    if not data["company_name"]:
        errors.append("Company name is required.")
    check_length(data["company_name"], 100, "Company name", errors)
    check_length(data["industry"], 50, "Industry", errors)
    check_length(data["website"], 200, "Website", errors)
    check_length(data["city"], 50, "City", errors)
    check_length(data["state"], 50, "State", errors)
    check_url(data["website"], "Website", errors)
    return data, errors


def validate_job(form):
    errors = []
    data = {f: clean(form, f) for f in ["company_id", "job_title", "job_type", "job_url"]}
    if not data["company_id"] or not db.get_company(data["company_id"]):
        errors.append("Please select a valid company.")
    if not data["job_title"]:
        errors.append("Job title is required.")
    check_length(data["job_title"], 100, "Job title", errors)
    if data["job_type"] and data["job_type"] not in JOB_TYPES:
        errors.append("Please select a valid job type.")
    check_length(data["job_url"], 300, "Job URL", errors)
    check_url(data["job_url"], "Job URL", errors)
    data["salary_min"] = check_int(clean(form, "salary_min"), "Minimum salary", errors)
    data["salary_max"] = check_int(clean(form, "salary_max"), "Maximum salary", errors)
    if (data["salary_min"] is not None and data["salary_max"] is not None
            and data["salary_min"] > data["salary_max"]):
        errors.append("Minimum salary cannot be greater than maximum salary.")
    data["date_posted"] = check_date(clean(form, "date_posted"), "Date posted", errors)
    data["requirements"] = parse_skills(form.get("requirements"))
    return data, errors


def validate_application(form):
    errors = []
    data = {f: clean(form, f) for f in ["job_id", "status", "resume_version"]}
    if not data["job_id"] or not db.get_job(data["job_id"]):
        errors.append("Please select a valid job.")
    data["application_date"] = check_date(
        clean(form, "application_date"), "Application date", errors, required=True)
    if data["application_date"] and data["application_date"] > date.today():
        errors.append("Application date cannot be in the future.")
    if data["status"] not in STATUSES:
        errors.append("Please select a valid status.")
    check_length(data["resume_version"], 50, "Resume version", errors)
    data["cover_letter_sent"] = form.get("cover_letter_sent") == "on"

    interview = {
        "interview_date": clean(form, "interview_date"),
        "interview_type": clean(form, "interview_type"),
        "interviewer": clean(form, "interviewer"),
        "notes": clean(form, "interview_notes"),
    }
    check_date(interview["interview_date"], "Interview date", errors)
    if interview["interview_type"] and interview["interview_type"] not in INTERVIEW_TYPES:
        errors.append("Please select a valid interview type.")
    data["interview_data"] = {k: v for k, v in interview.items() if v}
    return data, errors


def validate_contact(form):
    errors = []
    data = {f: clean(form, f) for f in
            ["company_id", "contact_name", "title", "email", "phone", "linkedin_url", "notes"]}
    if not data["company_id"] or not db.get_company(data["company_id"]):
        errors.append("Please select a valid company.")
    if not data["contact_name"]:
        errors.append("Contact name is required.")
    check_length(data["contact_name"], 100, "Contact name", errors)
    check_length(data["title"], 100, "Title", errors)
    check_length(data["email"], 100, "Email", errors)
    check_length(data["linkedin_url"], 200, "LinkedIn URL", errors)
    if data["email"] and not EMAIL_RE.match(data["email"]):
        errors.append("Please enter a valid email address.")
    if data["phone"] and not PHONE_RE.match(data["phone"]):
        errors.append("Phone may only contain digits, spaces, and + ( ) - . (7-20 characters).")
    check_url(data["linkedin_url"], "LinkedIn URL", errors)
    return data, errors


def abort_404():
    abort(404)


def flash_errors(errors):
    for error in errors:
        flash(error, "error")


def to_form_values(record):
    values = {}
    for key, value in record.items():
        if isinstance(value, date):
            values[key] = value.isoformat()
        elif value is None:
            values[key] = ""
        else:
            values[key] = value
    return values


# ----- Error handling -----

@app.errorhandler(mysql.connector.Error)
def handle_db_error(error):
    connection_problem = (isinstance(error, mysql.connector.InterfaceError)
                          or getattr(error, "errno", None) in CONNECTION_ERRORS)
    return render_template("dashboard.html", stats=None, db_error=str(error),
                           connection_problem=connection_problem), 500


@app.errorhandler(404)
def not_found(error):
    flash("The page or record you requested was not found.", "error")
    return redirect(url_for("dashboard"))


# ----- Dashboard -----

@app.route("/")
def dashboard():
    stats = db.get_dashboard_stats()
    total = stats["counts"]["applications"] or 0
    by_status = stats["by_status"]
    responded = sum(by_status.get(s, 0) for s in ["Screening", "Interview", "Offer"])
    stats["response_rate"] = round(responded / total * 100) if total else 0
    stats["active"] = total - by_status.get("Rejected", 0) - by_status.get("Withdrawn", 0)
    stats["offers"] = by_status.get("Offer", 0)
    return render_template("dashboard.html", stats=stats, statuses=STATUSES)


# ----- Companies CRUD -----

@app.route("/companies")
def companies():
    return render_template("companies.html", mode="list", companies=db.get_companies())


@app.route("/companies/<int:company_id>")
def company_detail(company_id):
    company = db.get_company(company_id) or abort_404()
    return render_template("companies.html", mode="detail", company=company,
                           jobs=db.get_jobs(company_id), contacts=db.get_contacts(company_id))


@app.route("/companies/add", methods=["GET", "POST"])
def company_add():
    if request.method == "POST":
        data, errors = validate_company(request.form)
        if not errors:
            db.add_company(data)
            flash(f"Company \"{data['company_name']}\" added.", "success")
            return redirect(url_for("companies"))
        flash_errors(errors)
    return render_template("companies.html", mode="form", item=request.form, editing=False)


@app.route("/companies/<int:company_id>/edit", methods=["GET", "POST"])
def company_edit(company_id):
    company = db.get_company(company_id) or abort_404()
    item = to_form_values(company)
    if request.method == "POST":
        data, errors = validate_company(request.form)
        if not errors:
            db.update_company(company_id, data)
            flash(f"Company \"{data['company_name']}\" updated.", "success")
            return redirect(url_for("company_detail", company_id=company_id))
        flash_errors(errors)
        item = request.form
    return render_template("companies.html", mode="form", item=item, editing=True,
                           record_id=company_id)


@app.route("/companies/<int:company_id>/delete", methods=["GET", "POST"])
def company_delete(company_id):
    company = db.get_company(company_id) or abort_404()
    if request.method == "GET":
        return render_template("companies.html", mode="delete", company=company,
                               jobs=db.get_jobs(company_id), contacts=db.get_contacts(company_id))
    db.delete_company(company_id)
    flash(f"Company \"{company['company_name']}\" and its related records were deleted.",
          "success")
    return redirect(url_for("companies"))


# ----- Jobs CRUD -----

def job_form_context(item, editing, record_id=None):
    return dict(mode="form", item=item, editing=editing, record_id=record_id,
                companies=db.get_companies(), job_types=JOB_TYPES)


@app.route("/jobs")
def jobs():
    return render_template("jobs.html", mode="list", jobs=db.get_jobs())


@app.route("/jobs/<int:job_id>")
def job_detail(job_id):
    job = db.get_job(job_id) or abort_404()
    return render_template("jobs.html", mode="detail", job=job,
                           applications=db.get_applications(job_id))


@app.route("/jobs/add", methods=["GET", "POST"])
def job_add():
    item = dict(request.form) if request.method == "POST" else {
        "company_id": request.args.get("company_id", "")}
    if request.method == "POST":
        data, errors = validate_job(request.form)
        if not errors:
            db.add_job(data)
            flash(f"Job \"{data['job_title']}\" added.", "success")
            return redirect(url_for("jobs"))
        flash_errors(errors)
    return render_template("jobs.html", **job_form_context(item, editing=False))


@app.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
def job_edit(job_id):
    job = db.get_job(job_id) or abort_404()
    item = to_form_values(job)
    item["requirements"] = ", ".join(job["requirements"])
    if request.method == "POST":
        data, errors = validate_job(request.form)
        if not errors:
            db.update_job(job_id, data)
            flash(f"Job \"{data['job_title']}\" updated.", "success")
            return redirect(url_for("job_detail", job_id=job_id))
        flash_errors(errors)
        item = request.form
    return render_template("jobs.html", **job_form_context(item, editing=True, record_id=job_id))


@app.route("/jobs/<int:job_id>/delete", methods=["GET", "POST"])
def job_delete(job_id):
    job = db.get_job(job_id) or abort_404()
    if request.method == "GET":
        return render_template("jobs.html", mode="delete", job=job,
                               applications=db.get_applications(job_id))
    db.delete_job(job_id)
    flash(f"Job \"{job['job_title']}\" and its applications were deleted.", "success")
    return redirect(url_for("jobs"))


# ----- Applications CRUD -----

def application_form_context(item, editing, record_id=None):
    return dict(mode="form", item=item, editing=editing, record_id=record_id,
                jobs=db.get_jobs(), statuses=STATUSES, interview_types=INTERVIEW_TYPES)


@app.route("/applications")
def applications():
    status = request.args.get("status")
    rows = db.get_applications()
    if status in STATUSES:
        rows = [r for r in rows if r["status"] == status]
    else:
        status = None
    return render_template("applications.html", mode="list", applications=rows,
                           statuses=STATUSES, current_status=status)


@app.route("/applications/<int:application_id>")
def application_detail(application_id):
    application = db.get_application(application_id) or abort_404()
    return render_template("applications.html", mode="detail", application=application)


@app.route("/applications/add", methods=["GET", "POST"])
def application_add():
    item = dict(request.form) if request.method == "POST" else {
        "job_id": request.args.get("job_id", ""),
        "application_date": date.today().isoformat(),
        "status": "Applied",
    }
    if request.method == "POST":
        data, errors = validate_application(request.form)
        if not errors:
            db.add_application(data)
            flash("Application added.", "success")
            return redirect(url_for("applications"))
        flash_errors(errors)
    return render_template("applications.html", **application_form_context(item, editing=False))


@app.route("/applications/<int:application_id>/edit", methods=["GET", "POST"])
def application_edit(application_id):
    application = db.get_application(application_id) or abort_404()
    item = to_form_values(application)
    interview = application["interview_data"]
    item.update({
        "interview_date": interview.get("interview_date", ""),
        "interview_type": interview.get("interview_type", ""),
        "interviewer": interview.get("interviewer", ""),
        "interview_notes": interview.get("notes", ""),
        "cover_letter_sent": "on" if application["cover_letter_sent"] else "",
    })
    if request.method == "POST":
        data, errors = validate_application(request.form)
        if not errors:
            db.update_application(application_id, data)
            flash("Application updated.", "success")
            return redirect(url_for("application_detail", application_id=application_id))
        flash_errors(errors)
        item = request.form
    return render_template("applications.html",
                           **application_form_context(item, editing=True,
                                                      record_id=application_id))


@app.route("/applications/<int:application_id>/delete", methods=["GET", "POST"])
def application_delete(application_id):
    application = db.get_application(application_id) or abort_404()
    if request.method == "GET":
        return render_template("applications.html", mode="delete", application=application)
    db.delete_application(application_id)
    flash("Application deleted.", "success")
    return redirect(url_for("applications"))


# ----- Contacts CRUD -----

def contact_form_context(item, editing, record_id=None):
    return dict(mode="form", item=item, editing=editing, record_id=record_id,
                companies=db.get_companies())


@app.route("/contacts")
def contacts():
    return render_template("contacts.html", mode="list", contacts=db.get_contacts())


@app.route("/contacts/<int:contact_id>")
def contact_detail(contact_id):
    contact = db.get_contact(contact_id) or abort_404()
    return render_template("contacts.html", mode="detail", contact=contact)


@app.route("/contacts/add", methods=["GET", "POST"])
def contact_add():
    item = dict(request.form) if request.method == "POST" else {
        "company_id": request.args.get("company_id", "")}
    if request.method == "POST":
        data, errors = validate_contact(request.form)
        if not errors:
            db.add_contact(data)
            flash(f"Contact \"{data['contact_name']}\" added.", "success")
            return redirect(url_for("contacts"))
        flash_errors(errors)
    return render_template("contacts.html", **contact_form_context(item, editing=False))


@app.route("/contacts/<int:contact_id>/edit", methods=["GET", "POST"])
def contact_edit(contact_id):
    contact = db.get_contact(contact_id) or abort_404()
    item = to_form_values(contact)
    if request.method == "POST":
        data, errors = validate_contact(request.form)
        if not errors:
            db.update_contact(contact_id, data)
            flash(f"Contact \"{data['contact_name']}\" updated.", "success")
            return redirect(url_for("contact_detail", contact_id=contact_id))
        flash_errors(errors)
        item = request.form
    return render_template("contacts.html",
                           **contact_form_context(item, editing=True, record_id=contact_id))


@app.route("/contacts/<int:contact_id>/delete", methods=["GET", "POST"])
def contact_delete(contact_id):
    contact = db.get_contact(contact_id) or abort_404()
    if request.method == "GET":
        return render_template("contacts.html", mode="delete", contact=contact)
    db.delete_contact(contact_id)
    flash(f"Contact \"{contact['contact_name']}\" deleted.", "success")
    return redirect(url_for("contacts"))


# ----- Job Match -----

def calculate_matches(user_skills, jobs_list):
    user_set = {skill.lower() for skill in user_skills}
    results = []
    for job in jobs_list:
        requirements = job.get("requirements") or []
        if not requirements:
            continue
        matched = [r for r in requirements if r.lower() in user_set]
        missing = [r for r in requirements if r.lower() not in user_set]
        if not matched:
            continue
        percent = round(len(matched) / len(requirements) * 100)
        results.append({
            "job": job,
            "matched": matched,
            "missing": missing,
            "total": len(requirements),
            "percent": percent,
        })
    results.sort(key=lambda r: (-r["percent"], -len(r["matched"]), r["job"]["job_title"]))
    return results


@app.route("/job-match", methods=["GET", "POST"])
def job_match():
    skills_text = request.form.get("skills", "") if request.method == "POST" else ""
    user_skills = parse_skills(skills_text)
    results = None
    if request.method == "POST":
        if not user_skills:
            flash("Please enter at least one skill.", "error")
        else:
            results = calculate_matches(user_skills, db.get_jobs_for_matching())
    all_skills = sorted({s for job in db.get_jobs_for_matching() for s in job["requirements"]},
                        key=str.lower)
    return render_template("job_match.html", skills_text=skills_text, user_skills=user_skills,
                           results=results, all_skills=all_skills)


if __name__ == "__main__":
    app.run(debug=True)
