import os
import sys
import json
import datetime
from sqlalchemy import create_engine, text

# Add backend directory to path if run from elsewhere
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from emailer.gmail_sender import send_email
from emailer.hotlist_template import generate_hotlist_html

def safe_print(text_to_print):
    try:
        print(text_to_print)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or 'utf-8'
        print(text_to_print.encode(encoding, errors='replace').decode(encoding))

def load_campaign_config():
    config_path = os.path.join(BASE_DIR, "campaigns_config.json")
    if not os.path.exists(config_path):
        print(f"Error: Configuration file not found at {config_path}")
        sys.exit(1)
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading configuration file: {e}")
        sys.exit(1)

def select_campaign(config):
    campaigns = config.get("campaigns", {})
    if not campaigns:
        print("Error: No campaigns found in configuration file.")
        sys.exit(1)
        
    print("\n==================================================")
    print("RECRUITFLOW-AI: HOTLIST EMAIL CAMPAIGN SELECTION")
    print("==================================================")
    campaign_keys = list(campaigns.keys())
    for idx, key in enumerate(campaign_keys, 1):
        campaign = campaigns[key]
        print(f"{idx}. {campaign.get('campaign_name')} (Subject: {campaign.get('subject')})")
        
    while True:
        try:
            choice = input(f"\nSelect a campaign (1-{len(campaign_keys)}): ").strip()
            if not choice:
                continue
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(campaign_keys):
                selected_key = campaign_keys[choice_idx]
                return campaigns[selected_key]
            else:
                print(f"Please select a number between 1 and {len(campaign_keys)}.")
        except (KeyboardInterrupt, SystemExit):
            print("\nExiting.")
            sys.exit(0)
        except ValueError:
            print("Please enter a valid number.")

def get_send_limit():
    while True:
        try:
            limit_input = input("\nEnter email sending limit for this run (default 50, range 1-500): ").strip()
            if not limit_input:
                return 50
            limit = int(limit_input)
            if 1 <= limit <= 500:
                return limit
            else:
                print("Please enter a number between 1 and 500.")
        except ValueError:
            print("Please enter a valid integer.")
        except (KeyboardInterrupt, SystemExit):
            print("\nExiting.")
            sys.exit(0)
def select_database():
    print("\n==================================================")
    print("RECRUITFLOW-AI: RECRUITER DATABASE SELECTION")
    print("==================================================")
    print("1. Sai Rushi Kasyap (jobs_rushi.db)")
    print("2. Santosh Anoushika Komala (jobs_anoushika.db)")
    print("3. Default / Legacy (jobs.db)")
    
    while True:
        try:
            choice = input("\nSelect recruiter list (1-3): ").strip()
            if choice == "1":
                return "jobs_rushi.db", "Sai Rushi Kasyap"
            elif choice == "2":
                return "jobs_anoushika.db", "Santosh Anoushika Komala"
            elif choice == "3":
                return "jobs.db", "Default/Legacy"
            else:
                print("Please select a number between 1 and 3.")
        except (KeyboardInterrupt, SystemExit):
            print("\nExiting.")
            sys.exit(0)
        except ValueError:
            print("Please enter a valid choice.")

def main():
    # Load configuration
    config = load_campaign_config()
    
    # Prompt for database choice
    db_filename, target_name = select_database()
    db_path = os.path.join(BASE_DIR, db_filename)
    
    if not os.path.exists(db_path):
        legacy_path = os.path.join(BASE_DIR, "jobs.db")
        if db_filename == "jobs_rushi.db" and os.path.exists(legacy_path):
            print(f"\nNote: jobs_rushi.db not found, falling back to legacy jobs.db")
            db_path = legacy_path
            db_filename = "jobs.db"
        else:
            print(f"\nDatabase file {db_path} does not exist yet. Please run the scraper first.")
            sys.exit(1)
            
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False, "timeout": 30.0}
    )
    
    # Prompt for campaign choice
    campaign = select_campaign(config)
    campaign_name = campaign.get("campaign_name")
    subject = campaign.get("subject")
    body_template = campaign.get("body")
    attachments = campaign.get("attachments", [])
    
    # Prompt for sending limit
    send_limit = get_send_limit()
    
    # Resolve attachment absolute paths relative to backend directory
    resolved_attachments = []
    for att in attachments:
        att_path = os.path.abspath(os.path.join(BASE_DIR, att))
        resolved_attachments.append(att_path)
        
    # Generate HTML content
    html_body = generate_hotlist_html(body_template)
    
    # Fetch unique recruiter emails from jobs table
    # Distinct emails to prevent duplicates in the same run
    print(f"\nFetching recruiter email addresses from {db_filename} for {target_name}...")
    recruiters = []
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT DISTINCT LOWER(TRIM(email)) FROM jobs WHERE email IS NOT NULL AND TRIM(email) != ''")
        )
        recruiters = [row[0] for row in result.fetchall() if row[0]]
        
    total_recruiters = len(recruiters)
    print(f"Total Unique Recruiters Found: {total_recruiters}")
    
    if total_recruiters == 0:
        print("No recruiters found in the database. Exiting.")
        return
        
    # Query hotlist_campaigns to find who already received this campaign
    already_sent_emails = set()
    with engine.connect() as conn:
        # Create table if not exists (redundancy check)
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS hotlist_campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recruiter_email TEXT,
                    campaign_name TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT
                )
                """
            )
        )
        conn.commit()
        
        result = conn.execute(
            text("SELECT DISTINCT LOWER(TRIM(recruiter_email)) FROM hotlist_campaigns WHERE campaign_name = :campaign_name AND status = 'sent'"),
            {"campaign_name": campaign_name}
        )
        already_sent_emails = {row[0] for row in result.fetchall() if row[0]}
        
    print(f"Already Sent in Previous Runs: {len(already_sent_emails)}")
    
    # Sending progress statistics
    stats = {
        "processed": 0,
        "already_sent": 0,
        "sent_success": 0,
        "failed": 0
    }
    
    # Open SMTP connection once for the entire campaign run
    import smtplib
    from emailer.gmail_sender import SMTP_SERVER, SMTP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD

    print("\nConnecting to SMTP server...")
    try:
        smtp_conn = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        smtp_conn.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    except Exception as smtp_err:
        print(f"Failed to connect/authenticate to SMTP server: {smtp_err}")
        return

    print("SMTP connection established successfully.")

    print("\nStarting Campaign Outbox Processing...")
    print("-" * 60)
    
    for email in recruiters:
        # Check limit of successfully sent emails in this run
        if stats["sent_success"] >= send_limit:
            print("-" * 60)
            print("Daily Gmail limit reached.")
            print("Campaign paused.\n")
            print(f"Sent today: {stats['sent_success']}")
            remaining = total_recruiters - len(already_sent_emails) - stats['sent_success']
            print(f"Remaining: {remaining}\n")
            print("Run this script again tomorrow to continue automatically.")
            print("-" * 60)
            break
            
        stats["processed"] += 1
        current_idx = stats["processed"]
        
        if email in already_sent_emails:
            stats["already_sent"] += 1
            print(f"Already Sent -> {email}")
            continue
            
        # Add a delay of 2 seconds between actual sends to avoid triggering SMTP abuse limits
        import time
        if stats["sent_success"] > 0 or stats["failed"] > 0:
            time.sleep(2)
            
        # Send marketing email
        print(f"Sending {current_idx}/{total_recruiters} to {email}...", end="", flush=True)
        
        try:
            # Send using our modified emailer module
            send_email(
                receiver=email,
                subject=subject,
                body=body_template,
                resume_path=None,  # We only send campaign attachments, not the default resume
                attachments=resolved_attachments,
                html_body=html_body,
                smtp_conn=smtp_conn
            )
            
            # Log success
            with engine.connect() as conn:
                conn.execute(
                    text("INSERT INTO hotlist_campaigns (recruiter_email, campaign_name, status) VALUES (:email, :campaign_name, 'sent')"),
                    {"email": email, "campaign_name": campaign_name}
                )
                conn.commit()
                
            stats["sent_success"] += 1
            print(" Sent Successfully")
            
        except Exception as e:
            err_msg = str(e)
            is_limit_exceeded = "5.4.5" in err_msg or "Daily user sending limit exceeded" in err_msg
            
            # Log failure
            with engine.connect() as conn:
                conn.execute(
                    text("INSERT INTO hotlist_campaigns (recruiter_email, campaign_name, status) VALUES (:email, :campaign_name, 'failed')"),
                    {"email": email, "campaign_name": campaign_name}
                )
                conn.commit()
                
            stats["failed"] += 1
            print(f" Failed: {e}")
            
            if is_limit_exceeded:
                print("-" * 60)
                print("Daily Gmail limit reached.")
                print("Campaign paused.\n")
                print(f"Sent today: {stats['sent_success']}")
                remaining = total_recruiters - len(already_sent_emails) - stats['sent_success']
                print(f"Remaining: {remaining}\n")
                print("Run this script again tomorrow to continue automatically.")
                print("-" * 60)
                break
            
    # Close SMTP connection cleanly at the end
    try:
        smtp_conn.quit()
    except Exception:
        pass

    print("-" * 60)
    print("Campaign Completed!")
    print(f"Total Recruiters: {total_recruiters}")
    print(f"Processed: {stats['processed']}/{total_recruiters}")
    print(f"Sent Successfully: {stats['sent_success']}")
    print(f"Already Sent: {stats['already_sent']}")
    print(f"Failed: {stats['failed']}")
    print("-" * 60)

if __name__ == "__main__":
    main()
