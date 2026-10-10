import json
import os
from reportlab_resume_maker import generate_resume_pdf

def update_anoushika_base():
    anoushika_data = {
        "name": "Santosh Anoushika Komala",
        "email": "anoushikakomala@gmail.com",
        "linkedin": "https://www.linkedin.com/in/anoushika-komala",
        "professional_summary": [
            "Cybersecurity Analyst with 1 Year hands-on experience in SOC Operations and security monitoring.",
            "Skilled in SIEM log analysis, alert investigation, and threat detection.",
            "Experienced in identifying and documenting Indicators of Compromise (IoCs).",
            "Hands-on experience with Incident Response and security incident documentation.",
            "Strong knowledge of Identity & Access Management (IAM) and RBAC.",
            "Experienced in Active Directory administration, account provisioning, and access reviews.",
            "Skilled in OSINT investigations and threat intelligence research.",
            "Experienced in vulnerability identification and security assessments.",
            "Proficient with Wireshark, Burp Suite, Ghidra, CyberChef, Shodan, and theHarvester.",
            "Knowledge of TCP/IP, DNS, DHCP, VPN, firewalls, and endpoint protection.",
            "Familiar with NIST, MITRE ATT&CK, defense-in-depth, and SOC security practices.",
            "Experienced in developing SOC runbooks, SOPs, and incident response procedures.",
            "Skilled in Python and AI/ML-based security analytics for fraud detection and malicious URL analysis.",
            "Exposure to AWS, Azure, and GCP security environments and authentication controls.",
            "Strong analytical, troubleshooting, technical documentation, communication, and cybersecurity problem-solving skills."
        ],
        "education": [
            {
                "degree": "Master of Science in Cybersecurity and Networks",
                "institution": "University of New Haven"
            }
        ],
        "technical_skills": {
            "SOC Operations": ["SOC Operations", "SIEM Log Analysis", "Threat Detection", "Threat Hunting", "Incident Response"],
            "IAM": ["Identity & Access Management", "Active Directory", "RBAC", "Account Provisioning", "Access Validation"],
            "Threat Intelligence": ["OSINT", "Fraud Research", "Vulnerability Identification", "Security Assessments"],
            "Tools": ["Wireshark", "Burp Suite", "Ghidra", "CyberChef", "Shodan", "theHarvester", "Python", "Exposure to SOAR", "SIEM"],
            "Networking": ["TCP/IP", "DNS", "DHCP", "VPN", "Endpoint Protection", "Firewall Concepts"],
            "Frameworks": ["NIST", "MITRE ATT&CK", "Incident Response Playbooks", "SOC Runbooks", "Defense-in-Depth"],
            "Cloud & AI": ["Applied AI-driven analytics for fraud detection", "AWS/Azure/GCP exposure"],
            "Soft Skills": ["Technical Documentation", "Collaboration", "Communication", "Troubleshooting", "SOP Development"]
        },
        "professional_experience": [
            {
                "company": "WeAfar Global Justice Inc.",
                "job_title": "Cyber Security Analyst",
                "duration": "October 2025 – Present",
                "description": [
                    "Monitor security events, alerts, system activity, and network traffic to identify potential security threats.",
                    "Analyze SIEM logs and investigate suspicious activities, anomalies, and Indicators of Compromise (IoCs).",
                    "Perform threat detection and basic threat-hunting activities across endpoints, applications, and network environments.",
                    "Investigate security incidents, document findings, and support incident response and remediation activities.",
                    "Manage IAM activities including RBAC, account provisioning, access reviews, and permission audits.",
                    "Administer Active Directory accounts, user permissions, password resets, and authentication controls.",
                    "Conduct OSINT and threat intelligence investigations to identify suspicious domains, IP addresses, and fraud infrastructure.",
                    "Perform vulnerability identification and security assessments for websites, applications, and systems.",
                    "Analyze network traffic using Wireshark to investigate security events and potential network-based threats.",
                    "Use Burp Suite for web application security testing and vulnerability identification.",
                    "Utilize Shodan, theHarvester, CyberChef, and Ghidra for reconnaissance, security research, analysis, and investigations.",
                    "Assist with endpoint hardening, patch management, firewall controls, VPN security, and endpoint protection.",
                    "Develop and maintain SOC runbooks, SOPs, incident response procedures, and technical security documentation.",
                    "Apply NIST and MITRE ATT&CK frameworks to support threat analysis, incident investigation, and security operations.",
                    "Collaborate with technical teams to troubleshoot security issues, communicate findings, and implement appropriate remediation measures.",
                    "Environment: SIEM, SOC Operations, IAM, Active Directory, RBAC, Incident Response, Threat Intelligence, OSINT, Vulnerability Assessment, Wireshark, Burp Suite, Ghidra, CyberChef, Shodan, theHarvester, Python, TCP/IP, DNS, DHCP, VPN, Firewalls, Endpoint Security, NIST, MITRE ATT&CK, Windows, AWS/Azure/GCP."
                ]
            },
            {
                "company": "University of New Haven",
                "job_title": "Graduate Assistant",
                "description": [
                    "Supported 300+ users across Windows, VPN, and network environments.",
                    "Managed Active Directory, IAM operations, and password resets.",
                    "Assisted with endpoint hardening and patch management."
                ]
            },
            {
                "company": "SmartKnower",
                "job_title": "AI & Security Intern",
                "description": [
                    "Developed ML-driven fraud detection models with 92% accuracy.",
                    "Conducted AI/cloud security assessments and supported authentication controls."
                ]
            },
            {
                "company": "Salesforce",
                "job_title": "Salesforce Developer Intern",
                "description": [
                    "Implemented RBAC and user access validation for secure CRM operations."
                ]
            }
        ],
        "projects": [
            {
                "title": "Capture the Flag Competitions & Cyber Defense",
                "description": [
                    "Participated in BSidesNYC, JerseyCTF, CIT CTF, and CBC competitions across web security, cryptography, forensics, reverse engineering, OSINT, and binary exploitation using Wireshark, Burp Suite, Ghidra, CyberChef, Shodan, theHarvester, and Python."
                ]
            },
            {
                "title": "SIEM Log Analysis",
                "description": [
                    "Detected anomalies and documented Indicators of Compromise (IoCs)."
                ]
            },
            {
                "title": "AI Security Models",
                "description": [
                    "Built ML models for spam and malicious URL detection with 92% accuracy."
                ]
            }
        ],
        "certifications": [
            "CompTIA Security+ (In Progress)",
            "CompTIA CySA+ (In Progress)",
            "Planned: Splunk Core User, Google SecOps, Microsoft SC-200"
        ]
    }

    # Hide job_description.txt temporarily so base PDF doesn't include duplicate JD
    jd_renamed = False
    if os.path.exists("job_description.txt"):
        os.rename("job_description.txt", "job_description.txt.tmp")
        jd_renamed = True

    try:
        os.makedirs("resumes", exist_ok=True)
        generate_resume_pdf(anoushika_data, "resumes/anoushika_base.pdf")
        print("Updated resumes/anoushika_base.pdf successfully.")
    finally:
        if jd_renamed and os.path.exists("job_description.txt.tmp"):
            os.rename("job_description.txt.tmp", "job_description.txt")

if __name__ == "__main__":
    update_anoushika_base()
