-- ----- Job Application Tracker - Database Creation Script -----

DROP DATABASE IF EXISTS job_tracker;
CREATE DATABASE job_tracker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE job_tracker;

-- ----- companies -----
CREATE TABLE companies (
    company_id   INT PRIMARY KEY AUTO_INCREMENT,
    company_name VARCHAR(100) NOT NULL,
    industry     VARCHAR(50),
    website      VARCHAR(200),
    city         VARCHAR(50),
    state        VARCHAR(50),
    notes        TEXT
) ENGINE=InnoDB;

-- ----- jobs -----
CREATE TABLE jobs (
    job_id       INT PRIMARY KEY AUTO_INCREMENT,
    company_id   INT,
    job_title    VARCHAR(100) NOT NULL,
    job_type     ENUM('Full-time','Part-time','Contract','Internship'),
    salary_min   INT,
    salary_max   INT,
    job_url      VARCHAR(300),
    date_posted  DATE,
    requirements JSON,
    CONSTRAINT fk_jobs_company
        FOREIGN KEY (company_id) REFERENCES companies(company_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ----- applications -----
CREATE TABLE applications (
    application_id    INT PRIMARY KEY AUTO_INCREMENT,
    job_id            INT,
    application_date  DATE NOT NULL,
    status            ENUM('Applied','Screening','Interview','Offer','Rejected','Withdrawn') DEFAULT 'Applied',
    resume_version    VARCHAR(50),
    cover_letter_sent BOOLEAN DEFAULT FALSE,
    interview_data    JSON,
    CONSTRAINT fk_applications_job
        FOREIGN KEY (job_id) REFERENCES jobs(job_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ----- contacts -----
CREATE TABLE contacts (
    contact_id   INT PRIMARY KEY AUTO_INCREMENT,
    company_id   INT,
    contact_name VARCHAR(100) NOT NULL,
    title        VARCHAR(100),
    email        VARCHAR(100),
    phone        VARCHAR(20),
    linkedin_url VARCHAR(200),
    notes        TEXT,
    CONSTRAINT fk_contacts_company
        FOREIGN KEY (company_id) REFERENCES companies(company_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ----- Sample data -----

INSERT INTO companies (company_name, industry, website, city, state, notes) VALUES
('TechCorp',        'Technology', 'https://www.techcorp.example.com',   'Miami',         'FL', 'Fast-growing software company with a strong engineering culture.'),
('DataCo',          'Analytics',  'https://www.dataco.example.com',     'Orlando',       'FL', 'Data consulting firm; hires many entry-level analysts.'),
('CloudNine Systems','Cloud Services','https://www.cloudnine.example.com','Austin',      'TX', 'Remote-friendly. Great benefits.'),
('FinEdge Bank',    'Finance',    'https://www.finedge.example.com',    'New York',      'NY', 'Large bank building an internal tech team.'),
('HealthBridge',    'Healthcare', 'https://www.healthbridge.example.com','Tampa',        'FL', 'Healthcare tech startup, Series B.');

INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max, job_url, date_posted, requirements) VALUES
(1, 'Software Developer',        'Full-time',  75000, 95000,  'https://www.techcorp.example.com/careers/101',  '2026-10-01', '["Python", "SQL", "Flask"]'),
(2, 'Data Analyst',              'Full-time',  60000, 75000,  'https://www.dataco.example.com/jobs/22',        '2026-10-05', '["Python", "SQL", "Tableau"]'),
(1, 'Junior Web Developer',      'Internship', 20000, 30000,  'https://www.techcorp.example.com/careers/115',  '2026-10-12', '["HTML", "CSS", "JavaScript", "Flask"]'),
(3, 'Cloud Engineer',            'Full-time',  90000, 120000, 'https://www.cloudnine.example.com/jobs/7',      '2026-09-28', '["AWS", "Linux", "Python", "Docker"]'),
(4, 'Database Administrator',    'Contract',   70000, 90000,  'https://www.finedge.example.com/careers/dba',   '2026-10-15', '["SQL", "MySQL", "Linux"]'),
(5, 'Backend Developer',         'Full-time',  80000, 100000, 'https://www.healthbridge.example.com/jobs/12',  '2026-10-20', '["Python", "Flask", "MySQL", "REST APIs"]'),
(2, 'Business Intelligence Intern','Internship',18000, 25000, 'https://www.dataco.example.com/jobs/31',        '2026-10-25', '["Excel", "SQL", "Power BI"]'),
(4, 'Full Stack Developer',      'Part-time',  40000, 55000,  'https://www.finedge.example.com/careers/fs',    '2026-11-01', '["JavaScript", "React", "Python", "SQL", "Git"]');

INSERT INTO applications (job_id, application_date, status, resume_version, cover_letter_sent, interview_data) VALUES
(1, '2026-10-03', 'Interview', 'v2.1-software', TRUE,
    '{"interview_date": "2026-10-20", "interview_type": "Video", "interviewer": "Maria Lopez", "notes": "Technical round went well; follow-up onsite expected."}'),
(2, '2026-10-07', 'Screening', 'v2.0-data',     TRUE,
    '{"interview_date": "2026-10-18", "interview_type": "Phone", "interviewer": "James Carter", "notes": "Recruiter phone screen."}'),
(3, '2026-10-14', 'Applied',   'v2.1-software', FALSE, NULL),
(4, '2026-10-01', 'Rejected',  'v1.5-general',  TRUE,
    '{"interview_date": "2026-10-10", "interview_type": "Phone", "interviewer": "Priya Shah", "notes": "Needed more AWS experience."}'),
(6, '2026-10-22', 'Offer',     'v2.1-software', TRUE,
    '{"interview_date": "2026-11-05", "interview_type": "On-site", "interviewer": "Daniel Kim", "notes": "Offer received! Respond by Nov 25."}'),
(7, '2026-10-27', 'Withdrawn', 'v2.0-data',     FALSE, NULL);

INSERT INTO contacts (company_id, contact_name, title, email, phone, linkedin_url, notes) VALUES
(1, 'Maria Lopez',  'Engineering Manager',   'maria.lopez@techcorp.example.com',  '305-555-0142', 'https://www.linkedin.com/in/marialopez',  'Met at FIU career fair.'),
(2, 'James Carter', 'Technical Recruiter',   'james.carter@dataco.example.com',   '407-555-0199', 'https://www.linkedin.com/in/jamescarter', 'Very responsive over email.'),
(3, 'Priya Shah',   'Senior Cloud Engineer', 'priya.shah@cloudnine.example.com',  '512-555-0110', 'https://www.linkedin.com/in/priyashah',   'Suggested getting AWS certified.'),
(5, 'Daniel Kim',   'CTO',                   'daniel.kim@healthbridge.example.com','813-555-0133', 'https://www.linkedin.com/in/danielkim',   'Hiring manager for backend role.'),
(4, 'Ashley Brown', 'HR Coordinator',        'ashley.brown@finedge.example.com',  '212-555-0177', NULL,                                      'Contact for contract roles.');
