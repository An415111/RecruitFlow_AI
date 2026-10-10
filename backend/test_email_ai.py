from emailer.templates import generate_email

jd = """
Looking for SOC Analyst in Dallas, TX.
Key responsibilities:
- SIEM monitoring & incident response
- Threat hunting

📧 Email: zeal@jpitstaffing.com

📞 Number: 9295421434

#CyberSecurity #SOCAnalyst #CloudSecurity #InformationSecurity #C2C #ITRecruiting #TechJobs #Hiring

1
"""

print(
    generate_email(
        candidate_name="Santosh Anoushika Komala",
        recruiter_name="Sam",
        role="SOC Analyst",
        linkedin_post_url="https://www.linkedin.com/feed/update/urn:li:activity:123456789/",
        candidate_details="Location: West Haven, CT",
        job_description=jd
    )
)