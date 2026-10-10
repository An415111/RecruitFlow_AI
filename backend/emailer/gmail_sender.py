import os
import smtplib

from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv(override=True)

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))



def send_email(
    receiver,
    subject,
    body,
    resume_path="resumes/Resumes.pdf",
    cc=None,
    bcc=None,
    attachments=None,
    html_body=None,
    smtp_conn=None,
    attachment_filename=None
):

    msg = EmailMessage()

    msg["From"] = EMAIL_ADDRESS
    msg["To"] = receiver
    
    if cc:
        if isinstance(cc, list):
            msg["Cc"] = ", ".join(cc)
        else:
            msg["Cc"] = cc
            
    if bcc:
        if isinstance(bcc, list):
            msg["Bcc"] = ", ".join(bcc)
        else:
            msg["Bcc"] = bcc
            
    msg["Subject"] = subject

    msg.set_content(body)
    
    if html_body:
        msg.add_alternative(html_body, subtype="html")

    # Gather all unique attachments
    all_attachments = list(attachments) if attachments else []
    if resume_path and resume_path not in all_attachments:
        all_attachments.append(resume_path)

    for filepath in all_attachments:
        if not filepath or not os.path.exists(filepath):
            print(f"WARNING: Attachment not found or empty: {filepath}")
            continue
            
        # Override filename if attachment_filename is provided and this is the resume attachment
        is_resume = False
        if filepath:
            if filepath == resume_path:
                is_resume = True
            elif resume_path and os.path.abspath(filepath) == os.path.abspath(resume_path):
                is_resume = True
            elif os.path.basename(filepath).lower() == "resumes.pdf":
                is_resume = True

        if attachment_filename and is_resume:
            filename = attachment_filename
        else:
            filename = os.path.basename(filepath)
            
        print(f"ATTACHING: {filepath} as {filename}")
        
        # Determine MIME type
        import mimetypes
        mime_type, _ = mimetypes.guess_type(filepath)
        if mime_type:
            maintype, subtype = mime_type.split("/", 1)
        else:
            maintype, subtype = "application", "octet-stream"
            
        with open(filepath, "rb") as f:
            file_data = f.read()
            msg.add_attachment(
                file_data,
                maintype=maintype,
                subtype=subtype,
                filename=filename
            )

    if smtp_conn:
        smtp_conn.send_message(msg)
    else:
        with smtplib.SMTP_SSL(
            SMTP_SERVER,
            SMTP_PORT
        ) as smtp:

            smtp.login(
                EMAIL_ADDRESS,
                EMAIL_PASSWORD
            )

            smtp.send_message(msg)

