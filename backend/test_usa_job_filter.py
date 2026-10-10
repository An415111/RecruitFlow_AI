import os
import sys

# Ensure backend directory is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from linkedin.linkedin_scraper import is_usa_job_post

def run_tests():
    print("==================================================")
    print("RUNNING USA JOB FILTER UNIT TESTS")
    print("==================================================")

    test_cases = [
        # (post_text, email, expected_is_usa, description)
        (
            "Looking for Senior SOC Analyst in Dallas, TX. C2C / W2 contract position. Send resume to recruiter@usstaffing.com",
            "recruiter@usstaffing.com",
            True,
            "Valid USA Job (C2C, TX, US domain)"
        ),
        (
            "Hiring Cyber Security Analyst. Location: Remote (US). Work auth: OPT/H1B. Email: hr@techsolutions.com",
            "hr@techsolutions.com",
            True,
            "Valid USA Job (US Remote, OPT/H1B)"
        ),
        (
            "Position: Assistant Controller in New York, NY. Contact john@financecorp.com for details.",
            "john@financecorp.com",
            True,
            "Valid USA Job (NY location, standard US email)"
        ),
        (
            "Need Java Developer for project in Hyderabad. Contact HR at hr@company.co.in",
            "hr@company.co.in",
            False,
            "Non-USA Email Domain (.co.in)"
        ),
        (
            "Cybersecurity analyst needed in London office. Contact +44 20 7946 0912 or hr@ukjobs.co.uk",
            "hr@ukjobs.co.uk",
            False,
            "Non-USA Phone Code (+44) and Domain (.co.uk)"
        ),
        (
            "Urgently hiring SOC Analyst. Call +91-9876543210 or mail sam@agency.com",
            "sam@agency.com",
            False,
            "International Phone Code (+91)"
        ),
        (
            "Position: Accountant. Location: Bangalore. Salary: 12 LPA. Send resume to jobs@fintech.com",
            "jobs@fintech.com",
            False,
            "Non-USD Currency / Salary (12 LPA) and Offshore Location (Bangalore)"
        ),
        (
            "Hiring Data Analyst in Toronto, Canada. Pay: $80,000 CAD per year. Apply at info@canadatech.ca",
            "info@canadatech.ca",
            False,
            "Offshore Location (Toronto, Canada) and Non-USA TLD (.ca)"
        ),
        (
            "Immediate requirement for SOC Analyst in Manila, Philippines. Email recruiter@phjobs.ph",
            "recruiter@phjobs.ph",
            False,
            "Offshore Location (Manila) and Non-USA TLD (.ph)"
        ),
        (
            "Hiring Accounting Manager in Dubai, UAE. Tax-free AED 25,000/month. Contact hr@dubaifinance.ae",
            "hr@dubaifinance.ae",
            False,
            "Offshore Location (Dubai) and Non-USD Currency (AED)"
        )
    ]

    passed = 0
    failed = 0

    for idx, (post_text, email, expected_is_usa, description) in enumerate(test_cases, 1):
        is_usa, reason = is_usa_job_post(post_text, email)
        status = "PASS" if is_usa == expected_is_usa else "FAIL"
        
        if is_usa == expected_is_usa:
            passed += 1
            print(f"[PASS] Case {idx}: {description} -> is_usa={is_usa} ({reason})")
        else:
            failed += 1
            print(f"[FAIL] Case {idx}: {description} -> Expected {expected_is_usa}, got {is_usa} ({reason})")

    print("\n--------------------------------------------------")
    print(f"Results: {passed} PASSED, {failed} FAILED out of {len(test_cases)} tests.")
    print("--------------------------------------------------")

    assert failed == 0, f"{failed} test(s) failed!"

if __name__ == "__main__":
    run_tests()
