from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv(override=True)

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None


def optimize_resume(job_description, resume_text, candidate_profile=None):

    # previous prompt
    # prompt = f"""
# You are a Senior ATS Resume Writer and Technical Recruiter.


# =================================================
# CANDIDATE RESUME
# =================================================

# {resume_text}

# =================================================
# JOB DESCRIPTION
# =================================================

# {job_description}

# =================================================
# TASK
# =================================================

# Analyze the Job Description and customize the resume to improve ATS matching.

# You may:

# - Rewrite Professional Summary
# - Reorder Skills
# - Highlight relevant technologies already present
# - Improve project descriptions
# - Add relevant ATS keywords from JD

# IMPORTANT:

# Rewrite the PROFESSIONAL SUMMARY completely according to the Job Description.

# Rewrite PROJECT DESCRIPTIONS to emphasize the technologies, skills, responsibilities, and keywords mentioned in the Job Description.

# Do not keep the same wording from the original resume.

# If the role is Java Developer, emphasize:
# - Java
# - Backend Development
# - REST APIs
# - Database Interaction
# - Problem Solving

# If the role is Python Developer, emphasize:
# - Python
# - Automation
# - APIs
# - FastAPI
# - Backend Development

# If the role is Data Analyst, emphasize:
# - SQL
# - Data Analysis
# - Reporting
# - Data Processing

# If the role is Business Analyst, emphasize:
# - Requirements Gathering
# - Stakeholder Communication
# - Documentation
# - Analysis

# If the role is Project Manager, emphasize:
# - Project Coordination
# - Team Collaboration
# - Communication
# - Delivery Management

# =================================================
# CRITICAL RULES
# =================================================

# Candidate is a Fresher.

# NEVER add:

# - 1+ years experience
# - 2+ years experience
# - 3+ years experience
# - 5+ years experience
# - 7+ years experience
# - 10+ years experience
# - 13+ years experience

# NEVER write:

# - Senior Developer
# - Lead Developer
# - Principal Engineer
# - Architect

# NEVER add:

# - Fake companies
# - Fake employment history
# - Fake certifications
# - Fake projects
# - Fake degrees
# - Fake achievements
# - Fake percentages
# - Fake impact numbers

# Treat all projects as personal/student projects.

# Only use technologies already present in the resume:

# Python
# Java
# JavaScript
# HTML
# CSS
# Node.js
# Express.js
# MongoDB
# SQLite
# FastAPI
# Git
# GitHub
# Playwright
# Telegram Bot API
# Cloudinary

# Do NOT add:

# AWS
# Azure
# GCP
# Kafka
# Bloomberg
# Django
# Angular
# React
# Spring Boot

# unless already present in the original resume.

# =================================================
# OUTPUT RULES
# =================================================

# Return ONLY the resume.

# Do NOT write:

# - Based on the provided Job Description
# - Job Description Analysis
# - Resume Rewrite
# - Notes
# - Explanation
# - Here is the optimized resume
# - RETURN FORMAT

# Start directly with:

# Ankit Gupta

# Email: ankitssgupta0786@gmail.com
# Phone: +91 9833250407
# Location: Mumbai, India
# LinkedIn: https://www.linkedin.com/in/ankit-gupta018/
# GitHub: https://github.com/An415111

# Sections:

# PROFESSIONAL SUMMARY

# TECHNICAL SKILLS

# PROJECTS

# EDUCATION

# CERTIFICATIONS

# ATS KEYWORDS MATCHED

# Do NOT include ATS SCORE.
# """
    
    # new prompt test 1
#     prompt = f"""
#     You are a Senior ATS Resume Writer, Technical Recruiter, and Hiring Manager with expertise in ATS systems (Workday, Greenhouse, Lever, Taleo, SuccessFactors).

# =================================================
# CANDIDATE RESUME
# ================

# {resume_text}

# =================================================
# JOB DESCRIPTION
# ===============

# {job_description}

# =================================================
# OBJECTIVE
# =========

# Analyze the Job Description internally and silently. Do not show the analysis. Use the analysis only to generate the final ATS-optimized resume.

# Your goal is to make the resume appear highly relevant to the target role without inventing any experience, skills, certifications, projects, achievements, or employment history.

# =================================================
# JOB DESCRIPTION ANALYSIS
# ========================

# Before rewriting the resume, internally identify:

# * Target Role
# * Required Skills
# * Preferred Skills
# * Responsibilities
# * Technical Keywords
# * Soft Skills
# * ATS Keywords
# * Industry Terminology

# Use these findings to optimize the resume.

# =================================================
# CUSTOMIZATION TASKS
# ===================

# 1. Rewrite PROFESSIONAL SUMMARY completely.

# Requirements:

# * Tailor it specifically to the target role.
# * Mention the most relevant technologies already present in the resume.
# * Include important ATS keywords from the Job Description.
# * Position the candidate as a motivated Fresher/Student/Early-Career Candidate.
# * Emphasize projects, technical skills, problem-solving, learning ability, and academic experience.

# 2. Optimize TECHNICAL SKILLS.

# * Reorder skills based on relevance to the Job Description.
# * Move JD-relevant skills to the top.
# * Remove duplicate skills.
# * Do not add technologies not present in the original resume.

# 3. Rewrite PROJECT DESCRIPTIONS.

# For each project:

# * Rewrite all bullet points.
# * Emphasize technologies relevant to the Job Description.
# * Highlight implementation details.
# * Highlight problem-solving.
# * Highlight technical complexity.
# * Highlight measurable functionality only if already supported by the resume.
# * Naturally integrate ATS keywords.

# Do NOT reuse the exact wording from the original resume.

# 4. Optimize Section Ordering.

# Prioritize:

# PROFESSIONAL SUMMARY

# TECHNICAL SKILLS

# PROJECTS

# EDUCATION

# CERTIFICATIONS

# ACHIEVEMENTS (if available)

# 5. ATS Keyword Integration.

# Naturally incorporate Job Description keywords throughout:

# * Summary
# * Skills
# * Projects

# Do NOT keyword stuff.

# =================================================
# ROLE-SPECIFIC OPTIMIZATION
# ==========================

# If target role is Java Developer:

# Emphasize:

# * Java
# * Object-Oriented Programming
# * Data Structures & Algorithms
# * Backend Development
# * REST APIs
# * Database Interaction
# * Problem Solving
# * Software Development

# If target role is Python Developer:

# Emphasize:

# * Python
# * Automation
# * FastAPI
# * Backend Development
# * APIs
# * Scripting
# * Data Processing

# If target role is Full Stack Developer:

# Emphasize:

# * JavaScript
# * Node.js
# * Express.js
# * MongoDB
# * REST APIs
# * Authentication
# * Frontend & Backend Development

# If target role is Backend Developer:

# Emphasize:

# * APIs
# * Server-side Development
# * Databases
# * Authentication
# * Scalability Concepts
# * Data Management

# If target role is Data Analyst:

# Emphasize:

# * SQL
# * Data Processing
# * Reporting
# * Data Analysis
# * Data Visualization (only if present)

# If target role is Business Analyst:

# Emphasize:

# * Analysis
# * Documentation
# * Stakeholder Communication
# * Requirements Gathering

# If target role is Project Coordinator / Project Manager:

# Emphasize:

# * Collaboration
# * Communication
# * Organization
# * Delivery Tracking
# * Coordination

# =================================================
# CRITICAL TRUTHFULNESS RULES
# ===========================

# Candidate is a Fresher.

# NEVER add:

# * 1+ years experience
# * 2+ years experience
# * 3+ years experience
# * 5+ years experience
# * 7+ years experience
# * 10+ years experience

# NEVER write:

# * Senior Developer
# * Lead Developer
# * Principal Engineer
# * Architect
# * Engineering Manager

# NEVER invent:

# * Companies
# * Internships
# * Employment History
# * Certifications
# * Skills
# * Technologies
# * Achievements
# * Publications
# * Awards
# * Metrics
# * Percentages
# * Impact Numbers

# Treat all projects as:

# * Academic Projects
# * Personal Projects
# * Student Projects

# Only use technologies that already exist in the candidate resume.

# =================================================
# TECHNOLOGY RESTRICTION
# ======================

# Use ONLY technologies found in the original resume.

# Do NOT introduce any new technology, framework, cloud platform, database, programming language, tool, or methodology that is not explicitly present in the candidate resume.

# =================================================
# ATS OPTIMIZATION RULES
# ======================

# * Use standard ATS section names.
# * No tables.
# * No columns.
# * No icons.
# * No graphics.
# * No emojis.
# * No text boxes.
# * No fancy formatting.
# * No headers/footers.
# * Use simple bullet points.
# * Ensure compatibility with major ATS systems.

# =================================================
# OUTPUT FORMAT
# =============

# Return ONLY the final ATS-optimized resume.

# Do NOT include:

# * Analysis
# * Explanation
# * Notes
# * Suggestions
# * ATS Score
# * Match Percentage
# * Resume Review
# * Improvement Recommendations
# * Job Description Analysis

# Start directly with:

# Ankit Gupta

# Email: [ankitssgupta0786@gmail.com](mailto:ankitssgupta0786@gmail.com)
# Phone: +91 9833250407
# Location: Mumbai, India
# LinkedIn: https://www.linkedin.com/in/ankit-gupta018/
# GitHub: https://github.com/An415111

# Required Sections:

# PROFESSIONAL SUMMARY

# TECHNICAL SKILLS

# PROJECTS

# EDUCATION

# CERTIFICATIONS

# ATS KEYWORDS MATCHED

# The ATS KEYWORDS MATCHED section must contain only keywords that appear in BOTH:

# 1. The Job Description
# 2. The Candidate Resume

# Do NOT include ATS SCORE.
# =================================================
# STRICT OUTPUT RULES
# ===================

# The final response MUST contain ONLY the ATS-optimized resume.

# DO NOT output:

# * Job Description Analysis
# * Target Role
# * Required Skills
# * Preferred Skills
# * ATS Analysis
# * Resume Review
# * Notes
# * Recommendations
# * Match Score
# * Explanation
# * Thinking Process
# * "Based on the provided job description"
# * "I will optimize the resume"
# * Any text before the candidate name

# Perform all analysis internally and silently.

# The first line of the response MUST be:

# Ankit Gupta

# The response must immediately continue with:

# Email:
# Phone:
# Location:
# LinkedIn:
# GitHub:

# Then directly generate these sections:

# PROFESSIONAL SUMMARY

# TECHNICAL SKILLS

# PROJECTS

# EDUCATION

# CERTIFICATIONS

# ATS KEYWORDS MATCHED

# Do NOT use markdown symbols such as:

# #

# ##

# ###

# **
# *

# >

# Do NOT wrap the resume inside code blocks.

# Do NOT include quotation marks.

# Return plain text only.

# If information is missing, leave the section concise instead of inventing details.

# Generate the complete resume from start to end.

    if candidate_profile is None:
        candidate_profile = {
            "name": "Sai Rushi Kasyap",
            "email": "rushimukkamala5@gmail.com",
            "phone": "+1 (346)-646-8149",
            "location": "Monroe, Michigan (Relocating)",
            "linkedin": "https://www.linkedin.com/in/rushi-mukkamala",
            "github": "",
            "education": [
                {
                    "degree": "Master of Science in Finance",
                    "institution": "University of Houston",
                    "duration": "Houston, TX",
                    "cgpa": ""
                },
                {
                    "degree": "Bachelor of Science in Accounting",
                    "institution": "",
                    "duration": "",
                    "cgpa": ""
                }
            ]
        }

    cand_name = candidate_profile.get("name", "Sai Rushi Kasyap")
    cand_email = candidate_profile.get("email", "rushimukkamala5@gmail.com")
    cand_phone = candidate_profile.get("phone", "+1 (346)-646-8149")
    cand_location = candidate_profile.get("location", "Monroe, Michigan (Relocating)")
    cand_linkedin = candidate_profile.get("linkedin", "https://www.linkedin.com/in/rushi-mukkamala")
    cand_github = candidate_profile.get("github", "")

    contact_details_prompt = f"""- name: "{cand_name}"
    - email: "{cand_email}"
    - phone: "{cand_phone}"
    - location: "{cand_location}"
    - linkedin: "{cand_linkedin}"
    - github: "{cand_github}"""

    education_list = candidate_profile.get("education", [])
    edu_instructions = ""
    for idx, edu in enumerate(education_list, 1):
        deg = edu.get("degree", "")
        inst = edu.get("institution", "")
        dur = edu.get("duration", "")
        cgpa = edu.get("cgpa", "")
        edu_instructions += f"       - degree {idx if idx > 1 else ''}: \"{deg}\"\n"
        if inst:
            edu_instructions += f"         institution: \"{inst}\"\n"
        if dur:
            edu_instructions += f"         duration: \"{dur}\"\n"
        if cgpa:
            edu_instructions += f"         cgpa: \"{cgpa}\"\n"

    education_schema_parts = []
    for edu in education_list:
        education_schema_parts.append({
            "degree": edu.get("degree", ""),
            "institution": edu.get("institution", ""),
            "duration": edu.get("duration", ""),
            "cgpa": edu.get("cgpa", "")
        })

    import json
    
    schema_dict = {
      "name": cand_name,
      "email": cand_email,
      "phone": cand_phone,
      "location": cand_location,
      "linkedin": cand_linkedin,
      "github": cand_github,
      "target_role": "",
      "professional_summary": ["", "", ""],
      "technical_skills": {
        "Programming Languages": [],
        "Databases": [],
        "Frameworks & Web Technologies": [],
        "Tools & Platforms": [],
        "Concepts": []
      },
      "professional_experience": [
        {
          "company": "",
          "location": "",
          "job_title": "",
          "duration": "",
          "description": ["", "", "", "", ""]
        }
      ],
      "projects": [
        {
          "title": "",
          "technologies": [],
          "description": ["", "", "", "", ""]
        }
      ],
      "education": education_schema_parts,
      "certifications": [],
      "achievements": [],
      "ats_keywords_matched": []
    }
    
    schema_str = json.dumps(schema_dict, indent=4)

    prompt = f"""
    You are a professional resume parsing and formatting assistant.
    Your sole task is to convert the candidate's base resume text into the exact JSON schema provided below.
    
    CRITICAL:
    - DO NOT customize, optimize, tailor, rewrite, or modify any bullet points, project descriptions, skills, or summaries based on the job description.
    - Keep all text, phrasing, achievements, and experiences 100% identical to the CANDIDATE BASE RESUME text.
    - Do NOT add any new skills or experience that are not in the base resume.
    - Do NOT remove any existing information.
    - The Job Description (JD) is provided ONLY to determine the "target_role" field (e.g. matching the job title of the JD) and to find matching keywords for the "ats_keywords_matched" field. Do not use the JD to change the content of the resume.

    Candidate contact details:
    {contact_details_prompt}

    =================================================
    CANDIDATE BASE RESUME
    =====================
    {resume_text}

    =================================================
    TARGET JOB DESCRIPTION (FOR REFERENCE ONLY to identify target_role)
    ===================================================================
    {job_description}

    =================================================
    JSON SCHEMA TO USE
    ==================
    {schema_str}
    
    Instructions for each field:
    1. "name", "email", "phone", "location", "linkedin", "github": Use the provided contact details.
    2. "target_role": Determine the target role title from the job description (e.g., matching the title of the JD).
    3. "professional_summary": Extract the professional summary from the base resume, split it into a list of strings (each string representing a sentence or logical line, keeping all wording identical).
    4. "technical_skills": Group the skills exactly as they are in the base resume under matching category keys. Preserve the categories and skill names exactly.
    5. "professional_experience": List all jobs from the base resume. For each job, keep the company, location, job_title, duration, and list of description bullets identical.
    6. "projects": List all projects from the base resume. For each project, keep the title, technologies, and list of description bullets identical.
    7. "education": List education entries identical to the base resume.
    8. "certifications": List certifications identical to the base resume.
    9. "achievements": List achievements identical to the base resume.
    10. "ats_keywords_matched": List keywords from the candidate's base resume that are also present in the job description.

    Return ONLY valid JSON.
    Do NOT return markdown blocks (like ```json), explanations, notes, or additional text.
    The response must start with {{ and end with }}.
    """

    from ai.llm_client import call_llm
    import time

    last_error = None
    for attempt in range(3):
        try:
            result = call_llm(prompt, max_tokens=4096)

            # Clean LLM output to extract only the valid JSON block
            start_json = result.find('{')
            end_json = result.rfind('}')
            if start_json != -1 and end_json != -1:
                result = result[start_json:end_json+1]
            
            # Clean common JSON issues (e.g. trailing commas before } or ])
            import re
            cleaned_result = re.sub(r',\s*([}\]])', r'\1', result)
            
            # Validate JSON structure
            json.loads(cleaned_result)
            return cleaned_result.strip()

        except Exception as e:
            last_error = e
            print(f"\n[Attempt {attempt+1}/3 failed]: {e}")
            if attempt < 2:
                sleep_time = 6 + (attempt * 3)
                print(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)

    # If all retries failed, raise the last exception
    raise last_error