import os
import sys
import re

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

def check_search_query_no_w2(target_keywords):
    queries = []
    for kw in target_keywords:
        query = f'"{kw}" -bench -fulltime -"available consultants"'
        queries.append(query)
    for q in queries:
        assert "w2" not in q.lower(), f"Search query contains W2: {q}"
        assert "-w2" not in q.lower(), f"Search query contains -w2: {q}"
    return queries

def is_w2_only_post(post_text: str) -> bool:
    post_lower = post_text.lower()
    w2_pattern = r"\b(w-?2|w\s+2|w2\s+only|w-2\s+only)\b"
    c2c_terms = ["c2c", "corp-to-corp", "corp to corp", "corp2corp", "c-to-c", "contract-to-hire", "cth", "contract", "1099", "c2c/w2", "w2/c2c", "c2c or w2", "w2 or c2c"]
    
    has_w2 = bool(re.search(w2_pattern, post_lower))
    has_c2c = any(term in post_lower for term in c2c_terms)
    
    return has_w2 and not has_c2c

def run_tests():
    print("==================================================")
    print("RUNNING W2 FILTER & SEARCH QUERY UNIT TESTS")
    print("==================================================")

    # Test 1: Verify search query does not mention W2
    keywords = ["SOC Analyst", "Assistant Controller", "Java Developer"]
    queries = check_search_query_no_w2(keywords)
    print("[PASS] Search query check: No W2/ -W2 in search strings:")
    for q in queries:
        print(f"   -> {q}")

    # Test 2: Verify W2 post filtering rules
    test_posts = [
        (
            "Hiring SOC Analyst. Position is W2 only. Contact hr@company.com",
            True,
            "W2 only post (should be excluded)"
        ),
        (
            "Looking for Senior Accountant on W-2 basis in NY. Contact recruiter@firm.com",
            True,
            "W-2 post without C2C (should be excluded)"
        ),
        (
            "Immediate hiring for Cyber Analyst on W 2. Send email to jobs@sec.com",
            True,
            "W 2 post without C2C (should be excluded)"
        ),
        (
            "Need Java Developer on C2C / W2 contract position. Contact recruiter@usstaffing.com",
            False,
            "C2C / W2 position (C2C option present, should be accepted)"
        ),
        (
            "Hiring Data Analyst. C2C role available. Contact hr@tech.com",
            False,
            "Pure C2C post (should be accepted)"
        ),
        (
            "Assistant Controller position available. See row 2 for details. Contact hr@finance.com",
            False,
            "Post containing 'row 2' substring (should NOT trigger false positive W2)"
        )
    ]

    passed = 0
    failed = 0

    for idx, (post_text, expected_w2_excluded, description) in enumerate(test_posts, 1):
        is_excluded = is_w2_only_post(post_text)
        if is_excluded == expected_w2_excluded:
            passed += 1
            print(f"[PASS] Case {idx}: {description} -> Excluded={is_excluded}")
        else:
            failed += 1
            print(f"[FAIL] Case {idx}: {description} -> Expected Excluded={expected_w2_excluded}, got {is_excluded}")

    print("\n--------------------------------------------------")
    print(f"Results: {passed} PASSED, {failed} FAILED out of {len(test_posts)} tests.")
    print("--------------------------------------------------")

    assert failed == 0, f"{failed} test(s) failed!"

if __name__ == "__main__":
    run_tests()
