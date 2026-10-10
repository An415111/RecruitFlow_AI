
try:
    from save_emails import save_email
except ImportError:
    from linkedin.save_emails import save_email
from playwright.sync_api import sync_playwright, Error as PlaywrightError
import re
import time
import urllib.parse
import threading
import sys

stop_scraping = False

def listen_for_stop():
    global stop_scraping
    try:
        input()  # Blocks until user presses Enter
        stop_scraping = True
        print("\n[STOP TRIGGERED] Stop request received! Finalizing current card and stopping scraper...")
    except Exception:
        pass


def extract_emails(text):

    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

    return re.findall(pattern, text)


def extract_job_details(job_description, keyword):
    try:
        import json
        import sys
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(current_dir)
        if backend_dir not in sys.path:
            sys.path.append(backend_dir)
            
        from ai.llm_client import call_llm
        prompt = f"""
You are an expert technical recruiter.
Analyze the following LinkedIn job description/post and extract:
1. The exact Job Position Title/Name (e.g., "SOC Analyst", "Security Engineer", "Information Security Specialist", "Assistant Controller"). Use only the actual job position name.
2. The classified role category, choosing from: "SOC Analyst", "SOC Analyst L1", "SOC Analyst L2", "Cyber Security Analyst", "Information Security Analyst", "Security Operations Center Analyst", "Security Analyst", "IAM Analyst", "Identity and Access Management Analyst", "Active Directory Administrator", "SIEM Analyst", "Incident Response Analyst", "Threat Intelligence Analyst", "Threat Hunting Analyst", "Blue Team Analyst", "Vulnerability Management Analyst", "Cloud Security Analyst", "Cyber Defense Analyst", "Security Operations Engineer", "Junior Security Engineer", "Assistant Controller", "Assistant Controller Nonprofit", "Accounting Manager", "Finance Manager", "Financial Reporting Manager", "Senior Accountant", "Grant Accountant", "Nonprofit Accountant", "Fund Accountant", "Government Grants Accountant", "General Ledger Accountant", "Accounting Operations Manager", "Corporate Accountant", "Internal Controls Manager", "Financial Analyst", "Budget Analyst", "Controller", "Senior Accounting Manager", "Finance Business Partner", "Accounting & Finance Manager", "Business Analyst", "Data Analyst", "Project Manager", "Java Developer", "Python Developer", "Unknown".

Job Description:
{job_description}

Output Format:
Return ONLY a valid JSON object with the keys "job_title" and "role_category". Do not include any other keys, explanations, or code blocks.
Example:
{{"job_title": "Junior SOC Analyst", "role_category": "SOC Analyst"}}
"""
        raw = call_llm(prompt, temperature=0.0, max_tokens=100)
        start_json = raw.find('{')
        end_json = raw.rfind('}')
        if start_json != -1 and end_json != -1:
            raw = raw[start_json:end_json+1]
        data = json.loads(raw)
        title = data.get("job_title", "").strip()
        role = data.get("role_category", "").strip()
        if not title or len(title) > 60:
            title = keyword
        if not role:
            role = "Unknown"
        return title, role
    except Exception:
        return keyword, "Unknown"


def is_usa_job_post(post_text: str, email: str):
    """
    Validates if a job post is strictly targeting the USA.
    Returns tuple: (is_usa: bool, reason: str)
    """
    email_lower = email.strip().lower()
    post_lower = post_text.lower()

    # 1. Non-USA Email Top-Level Domains (TLDs)
    non_usa_tlds = (
        ".in", ".co.in", ".net.in", ".org.in", ".gen.in", ".ind.in",
        ".pk", ".co.pk", ".ph", ".com.ph", ".uk", ".co.uk", ".org.uk", ".me.uk",
        ".ca", ".au", ".com.au", ".org.au", ".sg", ".com.sg", ".ae", ".de",
        ".nl", ".ie", ".br", ".com.br", ".mx", ".za", ".co.za", ".nz", ".co.nz",
        ".fr", ".es", ".it", ".eg", ".vn", ".id", ".co.id", ".ng", ".com.ng",
        ".lk", ".bd", ".ke", ".sa", ".qa", ".kh", ".pl"
    )
    if any(email_lower.endswith(tld) for tld in non_usa_tlds):
        domain = email_lower.split('@')[-1] if '@' in email_lower else email_lower
        return False, f"Non-USA email domain ({domain})"

    # 2. International Phone Codes (Non-US/Canada)
    non_usa_phone_codes = [
        "+91", "+63", "+44", "+92", "+234", "+49", "+971", "+353",
        "+31", "+55", "+52", "+61", "+65", "+60", "+94", "+880",
        "+254", "+966", "+974", "+48", "+33", "+34", "+39", "+27"
    ]
    for code in non_usa_phone_codes:
        if code in post_lower:
            return False, f"Post contains international phone code ({code})"

    # 3. Non-USD Salary / Currency terms
    non_usd_currency_terms = [
        "₹", "inr", "lpa", "lakhs", "lakh", "£", "gbp", "€", "eur",
        "aed", "aud", "php", "pkr", "rupees", "cad"
    ]
    for term in non_usd_currency_terms:
        if term in ["₹", "£", "€"]:
            if term in post_lower:
                return False, f"Post contains non-USD currency symbol ({term})"
        else:
            if re.search(rf"\b{term}\b", post_lower):
                return False, f"Post contains non-USD currency/salary term ({term})"

    # 4. Explicit Non-US Locations in post body
    offshore_locations = [
        "india", "hyderabad", "bangalore", "bengaluru", "pune", "chennai", "mumbai",
        "noida", "gurgaon", "gurugram", "delhi", "kolkata", "ahmedabad", "kochi",
        "trivandrum", "indore", "chandigarh", "jaipur", "uk", "united kingdom",
        "london", "manchester", "birmingham", "germany", "berlin", "munich",
        "netherlands", "amsterdam", "ireland", "dublin", "poland", "warsaw",
        "canada", "toronto", "vancouver", "montreal", "australia", "sydney",
        "melbourne", "pakistan", "lahore", "karachi", "islamabad", "philippines",
        "manila", "nigeria", "lagos", "uae", "dubai", "abu dhabi", "singapore",
        "malaysia", "kuala lumpur", "brazil", "mexico", "south africa", "johannesburg",
        "cape town", "egypt", "cairo", "vietnam", "indonesia"
    ]

    location_patterns = [
        rf"(?:location|job location|work location|office|based in|hiring in|hiring for|position in)\s*[:\-]?\s*\b({'|'.join(offshore_locations)})\b",
        rf"\b({'|'.join(offshore_locations)})\s*(?:only|onsite|office|branch|location)\b"
    ]

    for pattern in location_patterns:
        match = re.search(pattern, post_lower)
        if match:
            if not any(us_override in post_lower for us_override in ["us remote", "remote us", "remote (us)", "remote - us", "usa remote", "hiring for us", "us client"]):
                return False, f"Post specifies offshore location ({match.group(0)})"

    # 5. USA Context Check
    us_indicators = [
        "usa", "united states", "us", "u.s.", "u.s.a.", "c2c", "corp-to-corp",
        "corp to corp", "w2", "1099", "h1b", "opt", "stem opt", "green card",
        "gc", "us citizen", "usc", "ead", "est", "cst", "pst", "mst", "edt",
        "cdt", "pdt", "mdt", "remote us", "us remote", "remote (us)", "onsite usa",
        "tx", "ca", "ny", "nj", "fl", "il", "ma", "ga", "nc", "va", "md", "oh",
        "pa", "wa", "co", "mi", "dallas", "austin", "chicago", "new york", "houston"
    ]

    has_us_indicator = any(re.search(rf"\b{re.escape(ind)}\b", post_lower) for ind in us_indicators)

    for loc in offshore_locations:
        if re.search(rf"\b{loc}\b", post_lower) and not has_us_indicator:
            return False, f"Post mentions offshore location '{loc}' without US work context"

    return True, "Valid USA Job"


def search_jobs():
    global stop_scraping

    # Load candidate profiles
    import json
    import os
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(current_dir)
    profiles_path = os.path.join(backend_dir, "candidate_profiles.json")
    
    try:
        with open(profiles_path, "r", encoding="utf-8") as f:
            profiles = json.load(f)
    except Exception as e:
        print(f"Error loading candidate_profiles.json: {e}")
        sys.exit(1)

    print("\n==================================================")
    print("RECRUITFLOW-AI: CLIENT SELECTION")
    print("==================================================")
    client_keys = list(profiles.keys())
    for idx, key in enumerate(client_keys, 1):
        name = profiles[key].get("name", key)
        print(f"{idx}. {name} ({key})")
    
    while True:
        try:
            choice = input(f"\nSelect a client (1-{len(client_keys)}): ").strip()
            if not choice:
                continue
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(client_keys):
                selected_client_id = client_keys[choice_idx]
                selected_client = profiles[selected_client_id]
                break
            else:
                print(f"Please select a number between 1 and {len(client_keys)}.")
        except ValueError:
            print("Please enter a valid number.")

    print(f"\nSelected Client: {selected_client['name']}")
    
    # Now ask for search keyword/role selection
    print("\n==================================================")
    print(f"JOB ROLE / KEYWORD SELECTION FOR {selected_client['name'].upper()}")
    print("==================================================")
    client_keywords = selected_client.get("keywords", [])
    print("0. Search all keywords")
    for idx, kw in enumerate(client_keywords, 1):
        print(f"{idx}. {kw}")
    
    custom_option_idx = len(client_keywords) + 1
    print(f"{custom_option_idx}. Enter custom job role / keyword manually")
        
    while True:
        try:
            kw_choice = input(f"\nSelect a job role / keyword (0-{custom_option_idx}): ").strip()
            if not kw_choice:
                continue
            kw_idx = int(kw_choice)
            if 0 <= kw_idx <= custom_option_idx:
                break
            else:
                print(f"Please select a number between 0 and {custom_option_idx}.")
        except ValueError:
            print("Please enter a valid number.")

    if kw_idx == 0:
        target_keywords = client_keywords
        print(f"\nWill search for all {len(client_keywords)} job roles.")
    elif kw_idx == custom_option_idx:
        custom_kw = input("\nEnter custom job role / keyword (e.g. 'Security Engineer'): ").strip()
        while not custom_kw or any(term in custom_kw.lower() for term in ["bench sales", "benchsales", "bench-sales"]):
            if not custom_kw:
                custom_kw = input("Input cannot be empty. Enter custom job role / keyword: ").strip()
            else:
                custom_kw = input("Searching for 'Bench Sales' is not allowed. Enter another job role / keyword: ").strip()
        target_keywords = [custom_kw]
        print(f"\nWill search specifically for custom role: {custom_kw}")
    else:
        target_keywords = client_keywords[kw_idx - 1:]
        print(f"\nWill search for keywords from index {kw_idx} to the end: {', '.join(target_keywords)}")

    # Build search list with queries and base keywords
    search_list = []
    for kw in target_keywords:
        # Construct search query with negative exclusions: -bench -fulltime -"available consultants"
        # IMPORTANT: Do NOT include 'w2' or '-w2' in the search query string.
        query = f'"{kw}" -bench -fulltime -"available consultants"'
        search_list.append((query, kw))

    # Start stop-listener thread
    stop_thread = threading.Thread(target=listen_for_stop, daemon=True)
    stop_thread.start()
    print("\n>>> PRESS ENTER IN THIS TERMINAL AT ANY TIME TO STOP THE SCRAPER CLEANLY.")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        context = browser.new_context(
            storage_state="linkedin_session.json",
            permissions=["clipboard-read", "clipboard-write"]
        )

        page = context.new_page()

        page.goto(
            "https://www.linkedin.com/feed/",
            wait_until="domcontentloaded"
        )

        time.sleep(5)

        print("\nLinkedIn session loaded successfully!")

        saved_emails = set()

        for keyword, base_keyword in search_list:
            if stop_scraping:
                print("Stopping scraper: Stop requested.")
                break

            print(f"\nSearching: {keyword}")

            # Properly URL-encode the search query
            import urllib.parse
            encoded_query = urllib.parse.quote(keyword)
            search_url = f"https://www.linkedin.com/search/results/content/?keywords={encoded_query}&sortBy=%22date_posted%22&datePosted=%22past-24h%22"

            try:
                page.goto(search_url, wait_until="domcontentloaded", timeout=120000)
            except Exception as e:
                print(f"Failed loading {keyword}: {e}")
                continue

            time.sleep(5)

            # Fast check if no results found on page to skip scrolling
            try:
                no_results = page.locator("span:has-text('No results found'), h2:has-text('No results found'), h3:has-text('No results found'), h1:has-text('No results found'), .search-reusables__no-results-image")
                if no_results.count() > 0:
                    print(f"No results found on page for: {keyword}. Moving to next keyword.")
                    continue
            except Exception:
                pass

            scroll_count = 35 if selected_client_id in ("anoushika", "rushi") else 15
            print(f"Scrolling ({scroll_count} times)...")
            for _ in range(scroll_count):
                if stop_scraping:
                    break
                page.mouse.wheel(0, 3000)
                time.sleep(2)

            try:
                # Locate all post cards
                post_cards = page.locator("div[role='listitem'], li.reusable-search__result-container")
                card_count = post_cards.count()
                print(f"\nFound {card_count} post cards for keyword: {keyword}")

                for idx in range(card_count):
                    if stop_scraping:
                        print("Stopping scraper: Stop requested.")
                        break
                    post_card = post_cards.nth(idx)
                    
                    try:
                        # Scroll card into view
                        post_card.scroll_into_view_if_needed()
                        time.sleep(1)
                        
                        # Click "... more" button to expand full text if it exists
                        more_btn = post_card.locator("button:has-text('… more'), button:has-text('more')")
                        if more_btn.count() > 0:
                            try:
                                more_btn.first.click(timeout=2000)
                                time.sleep(0.5)
                            except Exception:
                                pass
                        
                        # Extract full text of the post safely
                        try:
                            post_text_raw = post_card.inner_text()
                        except Exception as e:
                            print(f"  - Card {idx+1}: Skipping (Could not extract post text: {e})")
                            continue

                        if post_text_raw is None or not post_text_raw.strip():
                            print(f"  - Card {idx+1}: Skipping (Post text is empty/None)")
                            continue

                        post_text = post_text_raw.strip()
                        post_lower = post_text.lower()
                        
                        # Filter by post age (past 24h only)
                        is_older_than_24h = False
                        time_found = False
                        detected_time = ""
                        for line in post_text.split('\n')[:8]:
                            line_clean = line.strip()
                            # Look for relative time patterns (e.g. "19h •", "1w •", "2d •", "1mo •")
                            time_match = re.search(r'\b(\d+)(m|h|d|w|mo|y)\b\s*(?:•|\u2022)', line_clean)
                            if not time_match and len(line_clean) < 15:
                                time_match = re.search(r'\b(\d+)(m|h|d|w|mo|y)\b', line_clean)
                            
                            if time_match:
                                val = int(time_match.group(1))
                                unit = time_match.group(2)
                                detected_time = f"{val}{unit}"
                                time_found = True
                                if unit == 'd' and val > 1:
                                    is_older_than_24h = True
                                elif unit in ['w', 'mo', 'y']:
                                    is_older_than_24h = True
                                break
                                
                        if time_found and is_older_than_24h:
                            print(f"  - Card {idx+1}: Skipping (Post is older than 24 hours: {detected_time})")
                            continue
                        
                        # Extract email from the post
                        emails = extract_emails(post_text)
                        if not emails:
                            print(f"  - Card {idx+1}: Skipping (No email address found in post text)")
                            continue
                        
                        email = emails[0].lower()
                        if email in saved_emails:
                            print(f"  - Card {idx+1}: Skipping (Email '{email}' already processed in this run)")
                            continue
                        
                        saved_emails.add(email)

                        # Enforce strict USA-only job filtering
                        is_usa, skip_reason = is_usa_job_post(post_text, email)
                        if not is_usa:
                            print(f"Skipping -> {email} ({skip_reason})")
                            continue
                        
                        # Extract actual post URL
                        post_url = "Unknown"
                        
                        # 1. Try finding data-urn attribute directly on the card or its children
                        try:
                            post_urn = post_card.get_attribute("data-urn") or ""
                            if not post_urn:
                                urn_el = post_card.locator("[data-urn]").first
                                if urn_el.count() > 0:
                                    post_urn = urn_el.get_attribute("data-urn") or ""
                            if "urn:li:" in post_urn:
                                post_url = f"https://www.linkedin.com/feed/update/{post_urn}/"
                        except Exception:
                            pass
                        
                        # 2. Search for a direct link containing highlightedUpdateUrn or any URN
                        if post_url == "Unknown":
                            import urllib.parse
                            links = post_card.locator("a")
                            link_count = links.count()
                            for l_idx in range(link_count):
                                href = links.nth(l_idx).get_attribute("href") or ""
                                decoded_href = urllib.parse.unquote(href)
                                match = re.search(r"(urn:li:[a-zA-Z0-9_]+:\d+)", decoded_href)
                                if match:
                                    urn = match.group(1)
                                    post_url = f"https://www.linkedin.com/feed/update/{urn}/"
                                    break
                        
                        # 3. Try copying the link using the control menu as fallback
                        if post_url == "Unknown":
                            control_btn = post_card.locator("button[aria-label*='control menu' i], button[aria-label*='Control menu']")
                            if control_btn.count() > 0:
                                try:
                                    control_btn.first.click(timeout=2000)
                                    time.sleep(1)
                                    copy_btn = page.locator("span:has-text('Copy link to post'), span:has-text('Copy link'), button:has-text('Copy link to post'), button:has-text('Copy link'), p:has-text('Copy link to post'), p:has-text('Copy link')")
                                    if copy_btn.count() > 0:
                                        copy_btn.first.click(timeout=2000)
                                        time.sleep(1)
                                        post_url = page.evaluate("navigator.clipboard.readText()")
                                    else:
                                        page.keyboard.press("Escape")
                                except Exception as e:
                                    print(f"Error copying link for card {idx+1}: {e}")
                                    try:
                                        page.keyboard.press("Escape")
                                    except Exception:
                                        pass
                                    
                        # If still Unknown, check if we can fall back to the recruiter profile URL
                        if post_url == "Unknown":
                            for l_idx in range(link_count):
                                href = links.nth(l_idx).get_attribute("href") or ""
                                if "/in/" in href:
                                    post_url = href
                                    break
                                    
                        # Last fallback is the search URL
                        if post_url == "Unknown":
                            post_url = page.url
                            
                        # Skip very small snippets
                        if len(post_text) < 100:
                            print(f"Skipping -> {email} (Post text is too short: {len(post_text)} chars)")
                            continue
                            
                        # Extract exact Job Position Title and classified category using LLM
                        title, role_category = extract_job_details(post_text, base_keyword)
                                
                        post_lower = post_text.lower()

                        # Internal C2C filter check:
                        # Exclude posts that explicitly mention W2 (and do not offer C2C)
                        # Uses word-boundary regex to avoid false positives (e.g., "row 2", "view 2", "kw2")
                        w2_pattern = r"\b(w-?2|w\s+2|w2\s+only|w-2\s+only)\b"
                        c2c_terms = ["c2c", "corp-to-corp", "corp to corp", "corp2corp", "c-to-c", "contract-to-hire", "cth", "contract", "1099", "c2c/w2", "w2/c2c", "c2c or w2", "w2 or c2c"]
                        has_w2 = bool(re.search(w2_pattern, post_lower))
                        has_c2c = any(term in post_lower for term in c2c_terms)
                        
                        if has_w2 and not has_c2c:
                            print(f"Skipping -> {email} (W2 job post excluded)")
                            continue

                        if selected_client_id == "anoushika":
                            # Cybersecurity keywords to check in post text as fallback
                            cyber_keywords = [
                                "soc", "cyber", "security", "iam", "siem", "incident response", 
                                "threat", "blue team", "vulnerability", "cloud security", 
                                "firewall", "sentinel", "splunk", "crowdstrike", "active directory",
                                "information security", "secops"
                            ]
                            
                            # Whitelist allowed cybersecurity roles for anoushika
                            allowed_cyber_roles = [
                                "SOC Analyst", "SOC Analyst L1", "SOC Analyst L2", "SOC Analyst L3",
                                "Cyber Security Analyst", "Information Security Analyst", 
                                "Security Operations Center Analyst", "Security Analyst", 
                                "IAM Analyst", "Identity and Access Management Analyst", 
                                "Active Directory Administrator", "SIEM Analyst", 
                                "Incident Response Analyst", "Threat Intelligence Analyst", 
                                "Threat Hunting Analyst", "Blue Team Analyst", 
                                "Vulnerability Management Analyst", "Cloud Security Analyst", 
                                "Cyber Defense Analyst", "Security Operations Engineer", 
                                "Junior Security Engineer", "Security Operations Center (SOC) Analyst", 
                                "Blue Team Security Analyst", "Security Engineer", "IT Security Analyst",
                                "Cyber Security Engineer", "Network Security Analyst", "Security Specialist",
                                "Information Security Specialist"
                            ]
                            
                            is_valid_cyber = role_category in allowed_cyber_roles or any(term in post_lower for term in cyber_keywords)
                            
                            if not is_valid_cyber:
                                print(f"Skipping -> {email} (Role category '{role_category}' does not match cybersecurity profile for anoushika)")
                                continue
                                
                            # Exclude senior / lead / offensive / architect roles for anoushika
                            title_lower = title.lower()
                            
                            # Senior / Lead / Manager / Architect terms
                            senior_terms = ["senior", "sr.", "lead", "principal", "staff", "director", "manager", "architect", "head", "chief", "vp"]
                            # Offensive / DevSecOps terms
                            offensive_terms = ["penetration", "pentester", "pen tester", "ethical hacker", "red team", "devsecops", "exploit"]
                            
                            is_senior = any(term in title_lower or f" {term} " in f" {title_lower} " for term in senior_terms)
                            is_offensive = any(term in title_lower for term in offensive_terms)
                            
                            if is_senior:
                                print(f"Skipping -> {email} (Title '{title}' is a Senior/Lead/Manager role, which does not match entry-level profile for anoushika)")
                                continue
                            if is_offensive:
                                print(f"Skipping -> {email} (Title '{title}' is an Offensive/DevSecOps role, which does not match defensive profile for anoushika)")
                                continue
                        elif selected_client_id == "rushi":
                            # Finance/Accounting keywords to check in post text as fallback
                            finance_keywords = [
                                "accounting", "accountant", "finance", "financial", "controller", 
                                "ledger", "audit", "budget", "reporting", "reconciliation", 
                                "gaap", "payroll", "billing", "ap/ar", "treasury", "quickbooks", "netsuite"
                            ]
                            
                            allowed_rushi_roles = [
                                "Assistant Controller", "Assistant Controller Nonprofit", "Accounting Manager", 
                                "Finance Manager", "Financial Reporting Manager", "Senior Accountant", 
                                "Grant Accountant", "Nonprofit Accountant", "Fund Accountant", 
                                "Government Grants Accountant", "General Ledger Accountant", "Accounting Operations Manager", 
                                "Corporate Accountant", "Internal Controls Manager", "Financial Analyst", 
                                "Budget Analyst", "Controller", "Senior Accounting Manager", 
                                "Finance Business Partner", "Accounting & Finance Manager",
                                "Accountant", "Staff Accountant", "Financial Accountant", "Accounting Specialist",
                                "Finance Associate", "Accounts Payable Manager", "Accounts Receivable Manager"
                            ]
                            
                            is_valid_finance = role_category in allowed_rushi_roles or any(term in post_lower for term in finance_keywords)
                            
                            if not is_valid_finance:
                                print(f"Skipping -> {email} (Role category '{role_category}' does not match accounting/finance profile for rushi)")
                                continue
                                
                        print("\n====================")
                        print(f"TITLE: {title}")
                        print(f"EMAIL: {email}")
                        print(f"URL: {post_url}")
                        print(f"CONTENT: {post_text[:300]}...")
                        print("====================\n")
                        
                        save_email(
                            email=email,
                            title=title,
                            job_description=post_text,
                            url=post_url,
                            client=selected_client_id,
                            search_keyword=base_keyword
                        )
                    except PlaywrightError as pe:
                        # Target closed/browser disconnected - bubble up
                        raise pe
                    except Exception as card_err:
                        print(f"Error processing card {idx + 1}: {card_err}")
            except PlaywrightError as pe:
                print(f"\nBrowser connection closed: {pe}")
                break

        print("\nDone.")

        try:
            input("\nPress Enter to close browser...")
        except Exception:
            pass

        try:
            browser.close()
        except Exception:
            pass


if __name__ == "__main__":
    search_jobs()