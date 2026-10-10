import os
import sys
import json
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import engine, get_db, BASE_DIR
from models import Base, Job
from schemas import JobCreate
from send_to_recruiters import send_all

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RecruitFlow AI API",
    description="Automated AI Outreach & Recruiter Pipeline System",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_client_db_path(client_id: Optional[str] = None) -> str:
    if client_id and client_id.strip() and client_id.lower() not in ["all", "default"]:
        candidate_path = os.path.join(BASE_DIR, f"jobs_{client_id.lower().strip()}.db")
        if os.path.exists(candidate_path):
            return candidate_path
    return os.path.join(BASE_DIR, "jobs.db")


def query_db(db_path: str, query_str: str, params: tuple = ()):
    conn = sqlite3.connect(db_path, timeout=10.0)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query_str, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def execute_db(db_path: str, query_str: str, params: tuple = ()):
    conn = sqlite3.connect(db_path, timeout=10.0)
    cursor = conn.cursor()
    cursor.execute(query_str, params)
    conn.commit()
    last_id = cursor.lastrowid
    affected = cursor.rowcount
    conn.close()
    return last_id, affected


class JobPayload(BaseModel):
    title: str
    company: str
    email: str
    url: Optional[str] = ""
    job_description: Optional[str] = ""
    client: Optional[str] = "rushi"


class SendEmailPayload(BaseModel):
    client_id: Optional[str] = "rushi"
    limit: Optional[int] = 5


class EmailPreviewPayload(BaseModel):
    client_id: Optional[str] = "rushi"
    job_title: Optional[str] = "Software Engineer"
    company: Optional[str] = "Tech Corp"
    job_description: Optional[str] = "Looking for a software engineer with Python and SQL experience."


@app.get("/api/candidates")
def get_candidates():
    profiles_path = os.path.join(BASE_DIR, "candidate_profiles.json")
    if not os.path.exists(profiles_path):
        return {}
    try:
        with open(profiles_path, "r", encoding="utf-8") as f:
            profiles = json.load(f)
        return profiles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load candidate profiles: {str(e)}")


@app.get("/api/all-candidate-stats")
def get_all_candidate_stats():
    profiles_path = os.path.join(BASE_DIR, "candidate_profiles.json")
    profiles = {}
    if os.path.exists(profiles_path):
        try:
            with open(profiles_path, "r", encoding="utf-8") as f:
                profiles = json.load(f)
        except Exception:
            pass

    client_keys = list(profiles.keys())
    if "default" not in client_keys:
        client_keys.append("default")

    results = {}
    combined_total = 0
    combined_sent = 0

    for key in client_keys:
        db_path = get_client_db_path(key)
        profile = profiles.get(key, {})
        name = profile.get("name", "Default Leads" if key == "default" else key.capitalize())

        total = 0
        sent = 0
        if os.path.exists(db_path):
            try:
                t_rows = query_db(db_path, "SELECT COUNT(*) as count FROM jobs")
                total = t_rows[0]["count"] if t_rows else 0
                s_rows = query_db(db_path, "SELECT COUNT(*) as count FROM jobs WHERE sent = 1 OR sent = '1'")
                sent = s_rows[0]["count"] if s_rows else 0
            except Exception:
                pass

        pending = total - sent
        pct = round((sent / total * 100), 1) if total > 0 else 0.0

        combined_total += total
        combined_sent += sent

        results[key] = {
            "candidate_id": key,
            "name": name,
            "db_file": os.path.basename(db_path),
            "email": profile.get("email", ""),
            "work_auth": profile.get("work_auth", "N/A"),
            "location": profile.get("location", ""),
            "total_recruiters": total,
            "emails_sent": sent,
            "pending": pending,
            "sent_percentage": pct,
            "keywords": profile.get("keywords", [])[:5]
        }

    combined_pending = combined_total - combined_sent
    combined_pct = round((combined_sent / combined_total * 100), 1) if combined_total > 0 else 0.0

    return {
        "summary": {
            "total_recruiters": combined_total,
            "emails_sent": combined_sent,
            "pending": combined_pending,
            "sent_percentage": combined_pct,
            "total_candidates": len(client_keys)
        },
        "candidates": results
    }


@app.get("/api/stats")
def get_api_stats(client: Optional[str] = None):
    if client and client.lower() == "all":
        all_stats = get_all_candidate_stats()
        summary = all_stats["summary"]
        summary["client"] = "all"
        summary["db_file"] = "all_databases"
        return summary

    db_path = get_client_db_path(client)
    try:
        total_rows = query_db(db_path, "SELECT COUNT(*) as count FROM jobs")
        total = total_rows[0]["count"] if total_rows else 0

        sent_rows = query_db(db_path, "SELECT COUNT(*) as count FROM jobs WHERE sent = 1 OR sent = '1'")
        sent = sent_rows[0]["count"] if sent_rows else 0

        pending = total - sent
        percentage = round((sent / total * 100), 1) if total > 0 else 0

        return {
            "client": client or "default",
            "db_file": os.path.basename(db_path),
            "total_recruiters": total,
            "emails_sent": sent,
            "pending": pending,
            "sent_percentage": percentage
        }
    except Exception as e:
        return {
            "client": client or "default",
            "total_recruiters": 0,
            "emails_sent": 0,
            "pending": 0,
            "sent_percentage": 0,
            "error": str(e)
        }


@app.get("/api/jobs")
def get_api_jobs(
    client: Optional[str] = Query(None),
    status: Optional[str] = Query("all"),
    search: Optional[str] = Query(""),
    limit: int = Query(500, ge=1, le=2000),
    offset: int = Query(0, ge=0)
):
    profiles_path = os.path.join(BASE_DIR, "candidate_profiles.json")
    profiles = {}
    if os.path.exists(profiles_path):
        try:
            with open(profiles_path, "r", encoding="utf-8") as f:
                profiles = json.load(f)
        except Exception:
            pass

    target_clients = []
    if client and client.lower() == "all":
        target_clients = list(profiles.keys())
        if "default" not in target_clients:
            target_clients.append("default")
    else:
        target_clients = [client or "default"]

    combined_jobs = []

    where_clauses = []
    params = []

    if status == "sent":
        where_clauses.append("(sent = 1 OR sent = '1')")
    elif status == "unsent":
        where_clauses.append("(sent IS NULL OR sent = 0 OR sent = '0' OR sent = '')")

    if search and search.strip():
        term = f"%{search.strip()}%"
        where_clauses.append("(title LIKE ? OR company LIKE ? OR email LIKE ? OR search_keyword LIKE ?)")
        params.extend([term, term, term, term])

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    query_str = f"""
        SELECT id, title, company, email, url, job_description, sent, client, search_keyword
        FROM jobs
        {where_sql}
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    """

    for c_key in target_clients:
        db_path = get_client_db_path(c_key)
        c_profile = profiles.get(c_key, {})
        c_name = c_profile.get("name", "Default Leads" if c_key == "default" else c_key.capitalize())

        if os.path.exists(db_path):
            try:
                p_list = list(params)
                p_list.extend([limit, offset])
                rows = query_db(db_path, query_str, tuple(p_list))
                for j in rows:
                    j["sent"] = bool(j.get("sent"))
                    j["candidate_id"] = c_key
                    j["candidate_name"] = c_name
                    combined_jobs.append(j)
            except Exception:
                pass

    if client and client.lower() == "all":
        combined_jobs.sort(key=lambda x: x.get("id", 0), reverse=True)
        return combined_jobs[:limit]

    return combined_jobs


@app.get("/api/jobs/{job_id}")
def get_api_job(job_id: int, client: Optional[str] = Query(None)):
    db_path = get_client_db_path(client)
    rows = query_db(db_path, "SELECT * FROM jobs WHERE id = ?", (job_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Job record not found")
    job = rows[0]
    job["sent"] = bool(job.get("sent"))
    return job


@app.post("/api/jobs")
def create_api_job(payload: JobPayload):
    db_path = get_client_db_path(payload.client)
    try:
        last_id, _ = execute_db(
            db_path,
            """
            INSERT INTO jobs (title, company, email, url, job_description, sent, client)
            VALUES (?, ?, ?, ?, ?, 0, ?)
            """,
            (payload.title, payload.company, payload.email, payload.url or "", payload.job_description or "", payload.client or "")
        )
        return {
            "message": "Job added successfully",
            "id": last_id,
            "client": payload.client
        }
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="A job record with this recruiter email already exists.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/jobs/{job_id}")
def delete_api_job(job_id: int, client: Optional[str] = Query(None)):
    db_path = get_client_db_path(client)
    _, affected = execute_db(db_path, "DELETE FROM jobs WHERE id = ?", (job_id,))
    if affected == 0:
        raise HTTPException(status_code=404, detail="Job record not found")
    return {"message": "Job lead deleted successfully", "id": job_id}


@app.patch("/api/jobs/{job_id}/toggle-sent")
def toggle_sent_status(job_id: int, client: Optional[str] = Query(None)):
    db_path = get_client_db_path(client)
    rows = query_db(db_path, "SELECT sent FROM jobs WHERE id = ?", (job_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Job record not found")
    current_status = bool(rows[0]["sent"])
    new_status = 0 if current_status else 1
    execute_db(db_path, "UPDATE jobs SET sent = ? WHERE id = ?", (new_status, job_id))
    return {"message": "Status updated", "id": job_id, "sent": bool(new_status)}


@app.post("/api/send-emails")
def trigger_send_emails(payload: SendEmailPayload = Body(...)):
    try:
        client_id = payload.client_id or "rushi"
        limit = payload.limit or 5
        send_all(limit=limit, client_id=client_id)
        return {
            "status": "success",
            "message": f"Outreach campaign triggered for candidate '{client_id}' (limit: {limit}).",
            "client_id": client_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/preview-email")
def preview_email(payload: EmailPreviewPayload):
    try:
        from emailer.templates import generate_email
        profiles_path = os.path.join(BASE_DIR, "candidate_profiles.json")
        client_profile = {}
        if os.path.exists(profiles_path):
            with open(profiles_path, "r", encoding="utf-8") as f:
                profiles = json.load(f)
                client_profile = profiles.get(payload.client_id, {})

        edu_list = client_profile.get("education", [])
        edu_str = ""
        for edu in edu_list:
            edu_str += f"\n- {edu.get('degree', '')} from {edu.get('institution', '')} ({edu.get('duration', '')})"
        skills_str = ", ".join(client_profile.get("keywords", []))

        candidate_details = f"""Candidate Name: {client_profile.get('name', 'Candidate')}
Email: {client_profile.get('email', '')}
Phone: {client_profile.get('phone', '')}
Location: {client_profile.get('location', '')}
LinkedIn: {client_profile.get('linkedin', '')}
Open to Relocate: {client_profile.get('open_to_relocate', 'yes')}
Work Authorization: {client_profile.get('work_auth', 'not mentioned')}
Availability: {client_profile.get('availability', 'immediate')}
Employer: {client_profile.get('employer', '')}
Employer Number: {client_profile.get('employer_number', '')}
Education: {edu_str}
Key Skills/Keywords: {skills_str}"""

        candidate_name = client_profile.get("name", "Sai Rushi Kasyap")
        recruiter_name = "Hiring Manager"
        role = payload.job_title or "Position"
        linkedin_url = "https://linkedin.com"

        email_content = generate_email(
            candidate_name=candidate_name,
            recruiter_name=recruiter_name,
            role=role,
            linkedin_post_url=linkedin_url,
            candidate_details=candidate_details,
            job_description=payload.job_description or "Software Engineering position requiring experience"
        )
        return {
            "status": "success",
            "candidate": client_profile.get("name", payload.client_id),
            "email_preview": email_content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- LEGACY ENDPOINTS FOR BACKWARD COMPATIBILITY ---------------- #

@app.post("/jobs")
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    new_job = Job(
        title=job.title,
        company=job.company,
        email=job.email,
        url=job.url,
        job_description=job.job_description
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return {"message": "Job Added Successfully", "id": new_job.id}


@app.get("/jobs")
def get_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()


@app.post("/send-emails")
def send_emails():
    try:
        send_all(client_id="rushi", limit=5)
        return {"message": "Emails sent successfully"}
    except Exception as e:
        return {"error": str(e)}


@app.get("/stats")
def stats(db: Session = Depends(get_db)):
    total = db.query(Job).count()
    sent = db.query(Job).filter(Job.sent == True).count()
    return {"total_recruiters": total, "emails_sent": sent}


@app.get("/unsent")
def unsent_jobs(db: Session = Depends(get_db)):
    return db.query(Job).filter(Job.sent != True).all()


@app.get("/job/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    return db.query(Job).filter(Job.id == job_id).first()


# Mount frontend static files at root / so index.html, style.css, app.js resolve seamlessly
frontend_dir = os.path.join(os.path.dirname(BASE_DIR), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")