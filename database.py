# ----- Job Application Tracker - Database functions -----

import json

import mysql.connector

try:
    from config import DB_CONFIG
except ImportError:
    print("WARNING: config.py not found. Copy config.example.py to config.py "
          "and enter your MySQL password.")
    DB_CONFIG = {
        "host": "localhost",
        "user": "root",
        "password": "",
        "database": "job_tracker",
    }


def get_db():
    return mysql.connector.connect(**DB_CONFIG)


# ----- Generic helpers -----

def query_all(sql, params=()):
    conn = get_db()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        conn.close()


def query_one(sql, params=()):
    rows = query_all(sql, params)
    return rows[0] if rows else None


def execute(sql, params=()):
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def parse_json(value, default=None):
    if value is None or value == "":
        return default
    if isinstance(value, (bytes, bytearray)):
        value = value.decode("utf-8")
    if isinstance(value, str):
        try:
            return json.loads(value)
        except ValueError:
            return default
    return value


def to_json(value):
    return json.dumps(value) if value else None


# ----- Companies -----

def get_companies():
    return query_all(
        """SELECT c.*,
                  (SELECT COUNT(*) FROM jobs j WHERE j.company_id = c.company_id) AS job_count,
                  (SELECT COUNT(*) FROM contacts ct WHERE ct.company_id = c.company_id) AS contact_count
           FROM companies c
           ORDER BY c.company_name"""
    )


def get_company(company_id):
    return query_one("SELECT * FROM companies WHERE company_id = %s", (company_id,))


def add_company(data):
    return execute(
        """INSERT INTO companies (company_name, industry, website, city, state, notes)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (data["company_name"], data["industry"], data["website"],
         data["city"], data["state"], data["notes"]),
    )


def update_company(company_id, data):
    execute(
        """UPDATE companies
           SET company_name = %s, industry = %s, website = %s, city = %s, state = %s, notes = %s
           WHERE company_id = %s""",
        (data["company_name"], data["industry"], data["website"],
         data["city"], data["state"], data["notes"], company_id),
    )


def delete_company(company_id):
    execute("DELETE FROM companies WHERE company_id = %s", (company_id,))


# ----- Jobs -----

def _prepare_job(row):
    if row is not None:
        row["requirements"] = parse_json(row.get("requirements"), [])
    return row


def get_jobs(company_id=None):
    sql = """SELECT j.*, c.company_name
             FROM jobs j
             LEFT JOIN companies c ON j.company_id = c.company_id"""
    params = ()
    if company_id is not None:
        sql += " WHERE j.company_id = %s"
        params = (company_id,)
    sql += " ORDER BY j.date_posted DESC, j.job_id DESC"
    return [_prepare_job(r) for r in query_all(sql, params)]


def get_job(job_id):
    return _prepare_job(query_one(
        """SELECT j.*, c.company_name
           FROM jobs j
           LEFT JOIN companies c ON j.company_id = c.company_id
           WHERE j.job_id = %s""",
        (job_id,),
    ))


def add_job(data):
    return execute(
        """INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max,
                             job_url, date_posted, requirements)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (data["company_id"], data["job_title"], data["job_type"], data["salary_min"],
         data["salary_max"], data["job_url"], data["date_posted"], to_json(data["requirements"])),
    )


def update_job(job_id, data):
    execute(
        """UPDATE jobs
           SET company_id = %s, job_title = %s, job_type = %s, salary_min = %s, salary_max = %s,
               job_url = %s, date_posted = %s, requirements = %s
           WHERE job_id = %s""",
        (data["company_id"], data["job_title"], data["job_type"], data["salary_min"],
         data["salary_max"], data["job_url"], data["date_posted"], to_json(data["requirements"]),
         job_id),
    )


def delete_job(job_id):
    execute("DELETE FROM jobs WHERE job_id = %s", (job_id,))


def get_jobs_for_matching():
    return get_jobs()


# ----- Applications -----

def _prepare_application(row):
    if row is not None:
        row["interview_data"] = parse_json(row.get("interview_data"), {}) or {}
        row["cover_letter_sent"] = bool(row.get("cover_letter_sent"))
    return row


APPLICATION_SELECT = """SELECT a.*, j.job_title, j.company_id, c.company_name
                        FROM applications a
                        LEFT JOIN jobs j ON a.job_id = j.job_id
                        LEFT JOIN companies c ON j.company_id = c.company_id"""


def get_applications(job_id=None):
    sql = APPLICATION_SELECT
    params = ()
    if job_id is not None:
        sql += " WHERE a.job_id = %s"
        params = (job_id,)
    sql += " ORDER BY a.application_date DESC, a.application_id DESC"
    return [_prepare_application(r) for r in query_all(sql, params)]


def get_application(application_id):
    return _prepare_application(
        query_one(APPLICATION_SELECT + " WHERE a.application_id = %s", (application_id,))
    )


def add_application(data):
    return execute(
        """INSERT INTO applications (job_id, application_date, status, resume_version,
                                     cover_letter_sent, interview_data)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (data["job_id"], data["application_date"], data["status"], data["resume_version"],
         data["cover_letter_sent"], to_json(data["interview_data"])),
    )


def update_application(application_id, data):
    execute(
        """UPDATE applications
           SET job_id = %s, application_date = %s, status = %s, resume_version = %s,
               cover_letter_sent = %s, interview_data = %s
           WHERE application_id = %s""",
        (data["job_id"], data["application_date"], data["status"], data["resume_version"],
         data["cover_letter_sent"], to_json(data["interview_data"]), application_id),
    )


def delete_application(application_id):
    execute("DELETE FROM applications WHERE application_id = %s", (application_id,))


# ----- Contacts -----

CONTACT_SELECT = """SELECT ct.*, c.company_name
                    FROM contacts ct
                    LEFT JOIN companies c ON ct.company_id = c.company_id"""


def get_contacts(company_id=None):
    sql = CONTACT_SELECT
    params = ()
    if company_id is not None:
        sql += " WHERE ct.company_id = %s"
        params = (company_id,)
    sql += " ORDER BY ct.contact_name"
    return query_all(sql, params)


def get_contact(contact_id):
    return query_one(CONTACT_SELECT + " WHERE ct.contact_id = %s", (contact_id,))


def add_contact(data):
    return execute(
        """INSERT INTO contacts (company_id, contact_name, title, email, phone, linkedin_url, notes)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (data["company_id"], data["contact_name"], data["title"], data["email"],
         data["phone"], data["linkedin_url"], data["notes"]),
    )


def update_contact(contact_id, data):
    execute(
        """UPDATE contacts
           SET company_id = %s, contact_name = %s, title = %s, email = %s, phone = %s,
               linkedin_url = %s, notes = %s
           WHERE contact_id = %s""",
        (data["company_id"], data["contact_name"], data["title"], data["email"],
         data["phone"], data["linkedin_url"], data["notes"], contact_id),
    )


def delete_contact(contact_id):
    execute("DELETE FROM contacts WHERE contact_id = %s", (contact_id,))


# ----- Dashboard -----

def get_dashboard_stats():
    counts = query_one(
        """SELECT (SELECT COUNT(*) FROM companies)    AS companies,
                  (SELECT COUNT(*) FROM jobs)         AS jobs,
                  (SELECT COUNT(*) FROM applications) AS applications,
                  (SELECT COUNT(*) FROM contacts)     AS contacts"""
    )
    status_rows = query_all(
        "SELECT status, COUNT(*) AS count FROM applications GROUP BY status"
    )
    by_status = {row["status"]: row["count"] for row in status_rows}
    recent = get_applications()[:5]
    return {"counts": counts, "by_status": by_status, "recent": recent}
