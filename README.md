# Job Application Tracker

## Project Description

A web application for tracking job applications. It stores companies, job postings, applications, and contacts in a MySQL database, and includes a Job Match feature that ranks saved jobs by how well they match your skills.

## Technologies Used

- MySQL (database)
- Python 3 with Flask and mysql-connector-python (backend)
- HTML and CSS (frontend)

## Features

- Dashboard with statistics (totals, applications by status, response rate, recent applications)
- Full CRUD (list, view, add, edit, delete with confirmation) for Companies, Jobs, Applications, and Contacts, with form validation
- Job Match: enter your skills to see jobs ranked by match percentage, with missing skills listed

## Requirements

- Python 3
- MySQL Server
- MySQL Workbench (optional, for viewing the database)

## Setup Instructions

1. Clone the repository and open the project folder:
   ```
   git clone https://github.com/santiagosanchez5705/job-application-tracker.git
   cd job-application-tracker
   ```
2. Install the Python dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `config.example.py` to a new file named `config.py`, then replace `YOUR_PASSWORD` with your MySQL root password.
4. Create the database and sample data by running `schema.sql`, either in MySQL Workbench (File > Open SQL Script, then Execute) or from a terminal:
   ```
   mysql -u root -p < schema.sql
   ```
5. Start the application:
   ```
   python app.py
   ```
6. Open http://127.0.0.1:5000 in your browser.

## Project Structure

```
job-application-tracker/
├── app.py              # Flask application (routes, validation, Job Match)
├── database.py         # Database connection and query functions
├── config.example.py   # MySQL credentials template (copy to config.py)
├── schema.sql          # Database creation script with sample data
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
├── static/style.css    # Stylesheet
├── AI_USAGE.md         # GenAI usage documentation
└── README.md           # Project description and setup instructions
```

## Demo Video

<!-- Required by the instructions: a 3 to 7-minute recorded video of the project running (client, server, database), uploaded to GitHub. Put the video's file name here. -->

_(Write your video file name here)_
