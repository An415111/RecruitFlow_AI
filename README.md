# RecruitFlow AI

RecruitFlow AI is an automation tool that helps job seekers find recruiter emails from LinkedIn posts and automatically send resumes.

## Features

* Scrape LinkedIn recruiter posts using Playwright
* Extract recruiter email addresses
* Store emails in SQLite database
* View recruiter data using FastAPI APIs
* Send personalized emails with resume attachment
* Swagger UI integration for testing APIs

## Tech Stack

* Python
* FastAPI
* SQLite
* SQLAlchemy
* Playwright
* HTML
* CSS
* JavaScript

## API Endpoints

### GET /

Returns application status.

### POST /jobs

Add a job record.

### GET /jobs

Retrieve stored recruiter data.

### POST /send-emails

Send resume emails to recruiters stored in the database.

## Project Workflow

LinkedIn Posts → Email Extraction → SQLite Database → FastAPI API → Resume Attachment → Automated Email Sending

## Author

Ankit Gupta
BSc Computer Science
