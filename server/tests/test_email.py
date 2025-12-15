import asyncio
from datetime import date, timedelta
from app.core.email import email_service

# Test Configuration
TEST_EMAIL = "umairimran627@gmail.com"
PASSED = 0
FAILED = 0

def log_result(test_name: str, passed: bool, details: str = ""):
    """Log test result with color and details."""
    global PASSED, FAILED
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status} | {test_name}")
    if details:
        print(f"       Details: {details}")
    if passed:
        PASSED += 1
    else:
        FAILED += 1

# ==================== BASIC FUNCTIONALITY TESTS ====================

async def test_basic_email_plain_text():
    """Test basic plain text email."""
    print("\n[1] Testing basic plain text email...")
    ok = await email_service.send_email(
        to=[TEST_EMAIL],
        subject="Test Email from Dashboard",
        body="This is a test email. If you receive this, SMTP is working!",
        html=False,
    )
    log_result("Basic plain text email", ok)

async def test_basic_email_html():
    """Test basic HTML email."""
    print("\n[2] Testing basic HTML email...")
    ok = await email_service.send_email(
        to=[TEST_EMAIL],
        subject="HTML Test Email",
        body="<h1>HTML Email</h1><p>This email has <strong>HTML</strong> formatting.</p>",
        html=True,
    )
    log_result("Basic HTML email", ok)

async def test_multiple_recipients():
    """Test email with multiple recipients."""
    print("\n[3] Testing multiple recipients...")
    ok = await email_service.send_email(
        to=[TEST_EMAIL, TEST_EMAIL],  # Same email twice to test list handling
        subject="Multi-Recipient Test",
        body="Testing multiple recipients",
        html=False,
    )
    log_result("Multiple recipients", ok)

# ==================== EDGE CASES & BOUNDARY TESTS ====================

async def test_very_long_subject():
    """Test email with extremely long subject line."""
    print("\n[4] Testing very long subject (500 chars)...")
    long_subject = "A" * 500 + " - Testing Long Subject Line Handling"
    ok = await email_service.send_email(
        to=[TEST_EMAIL],
        subject=long_subject,
        body="Testing long subject line handling",
        html=False,
    )
    log_result("Very long subject (500 chars)", ok)

async def test_very_long_body():
    """Test email with extremely long body."""
    print("\n[5] Testing very long body (10K chars)...")
    long_body = "This is a test of a very long email body. " * 500  # ~10K chars
    ok = await email_service.send_email(
        to=[TEST_EMAIL],
        subject="Long Body Test",
        body=long_body,
        html=False,
    )
    log_result("Very long body (10K chars)", ok)

async def test_special_characters_in_subject():
    """Test special characters in subject."""
    print("\n[6] Testing special characters in subject...")
    ok = await email_service.send_email(
        to=[TEST_EMAIL],
        subject="Test: <>\"'&@#$%^*(){}[]|\\;:,.<>?/~`",
        body="Testing special characters handling",
        html=False,
    )
    log_result("Special characters in subject", ok)

async def test_unicode_and_emoji():
    """Test Unicode characters and emoji."""
    print("\n[7] Testing Unicode and emoji...")
    ok = await email_service.send_email(
        to=[TEST_EMAIL],
        subject="Unicode Test: 你好 مرحبا 🚀🔥💯",
        body="Testing Unicode: Привет, مرحبا, 你好, 안녕하세요 with emojis: 📧✉️📬📭",
        html=False,
    )
    log_result("Unicode and emoji support", ok)

async def test_html_injection_safety():
    """Test HTML injection safety."""
    print("\n[8] Testing HTML injection safety...")
    malicious_html = "<script>alert('XSS')</script><img src=x onerror=alert('XSS')>"
    ok = await email_service.send_email(
        to=[TEST_EMAIL],
        subject="HTML Injection Test",
        body=f"<p>Testing injection: {malicious_html}</p>",
        html=True,
    )
    log_result("HTML injection safety", ok, "Check email for script tags")

async def test_empty_body():
    """Test email with empty body."""
    print("\n[9] Testing empty body...")
    ok = await email_service.send_email(
        to=[TEST_EMAIL],
        subject="Empty Body Test",
        body="",
        html=False,
    )
    log_result("Empty body handling", ok)

async def test_newlines_and_formatting():
    """Test various newline and formatting characters."""
    print("\n[10] Testing newlines and formatting...")
    body = "Line 1\nLine 2\r\nLine 3\n\nLine 5\tTabbed content"
    ok = await email_service.send_email(
        to=[TEST_EMAIL],
        subject="Newline & Formatting Test",
        body=body,
        html=False,
    )
    log_result("Newlines and formatting", ok)

# ==================== ALERT-SPECIFIC TESTS ====================

async def test_ingestion_failure_alert_normal():
    """Test normal ingestion failure alert."""
    print("\n[11] Testing ingestion failure alert (normal)...")
    ok = await email_service.send_ingestion_failure_alert(
        client_name="Test Client",
        source="surfside",
        run_date=date.today(),
        error_message="Database connection timeout after 30 seconds",
        admin_emails=[TEST_EMAIL],
    )
    log_result("Ingestion failure alert (normal)", ok)

async def test_ingestion_failure_with_long_error():
    """Test ingestion failure with very long error message."""
    print("\n[12] Testing ingestion failure with long error...")
    long_error = "Critical error occurred: " + "Error details. " * 200  # ~3K chars
    ok = await email_service.send_ingestion_failure_alert(
        client_name="ACME Corp International LLC",
        source="surfside_extended_api_v2",
        run_date=date.today(),
        error_message=long_error,
        admin_emails=[TEST_EMAIL],
    )
    log_result("Ingestion failure with long error", ok)

async def test_ingestion_failure_special_chars():
    """Test ingestion failure with special characters."""
    print("\n[13] Testing ingestion failure with special chars...")
    ok = await email_service.send_ingestion_failure_alert(
        client_name="Client & Co. <Special>",
        source="facebook",
        run_date=date.today(),
        error_message="Error: 'Connection' failed at 'Auth' stage. Code: <500>",
        admin_emails=[TEST_EMAIL],
    )
    log_result("Ingestion failure with special chars", ok)

async def test_validation_error_alert_normal():
    """Test normal validation error alert."""
    print("\n[14] Testing validation error alert (normal)...")
    errors = [
        "Row 5: Missing required column 'Campaign'",
        "Row 12: Invalid date format '2025-13-45'",
        "Row 18: Impressions must be positive integer",
    ]
    ok = await email_service.send_validation_error_alert(
        client_name="Test Client",
        source="facebook",
        run_date=date.today(),
        errors=errors,
        admin_emails=[TEST_EMAIL],
    )
    log_result("Validation error alert (normal)", ok)

async def test_validation_error_many_errors():
    """Test validation error with many errors."""
    print("\n[15] Testing validation error with 100 errors...")
    errors = [f"Row {i}: Validation error #{i} - Data integrity issue" for i in range(1, 101)]
    ok = await email_service.send_validation_error_alert(
        client_name="Big Client",
        source="vibe",
        run_date=date.today(),
        errors=errors,
        admin_emails=[TEST_EMAIL],
    )
    log_result("Validation error with 100 errors", ok)

async def test_validation_error_empty_list():
    """Test validation error with empty error list."""
    print("\n[16] Testing validation error with empty list...")
    ok = await email_service.send_validation_error_alert(
        client_name="Test Client",
        source="facebook",
        run_date=date.today(),
        errors=[],
        admin_emails=[TEST_EMAIL],
    )
    log_result("Validation error with empty list", ok)

async def test_validation_error_special_chars():
    """Test validation error with special characters."""
    print("\n[17] Testing validation error with special chars...")
    errors = [
        "Row 1: Value '<script>' is invalid",
        "Row 2: Field \"Campaign\" has '&' character",
        "Row 3: Unicode error: 你好 is not allowed",
    ]
    ok = await email_service.send_validation_error_alert(
        client_name="Test Client",
        source="facebook",
        run_date=date.today(),
        errors=errors,
        admin_emails=[TEST_EMAIL],
    )
    log_result("Validation error with special chars", ok)

async def test_missing_file_alert_normal():
    """Test normal missing file alert."""
    print("\n[18] Testing missing file alert (normal)...")
    ok = await email_service.send_missing_file_alert(
        client_name="Test Client",
        source="vibe",
        expected_date=date.today(),
        admin_emails=[TEST_EMAIL],
    )
    log_result("Missing file alert (normal)", ok)

async def test_missing_file_alert_past_date():
    """Test missing file alert with past date."""
    print("\n[19] Testing missing file alert with past date...")
    past_date = date.today() - timedelta(days=30)
    ok = await email_service.send_missing_file_alert(
        client_name="Historical Client",
        source="surfside",
        expected_date=past_date,
        admin_emails=[TEST_EMAIL],
    )
    log_result("Missing file alert with past date", ok)

async def test_missing_file_alert_future_date():
    """Test missing file alert with future date."""
    print("\n[20] Testing missing file alert with future date...")
    future_date = date.today() + timedelta(days=7)
    ok = await email_service.send_missing_file_alert(
        client_name="Future Client",
        source="vibe",
        expected_date=future_date,
        admin_emails=[TEST_EMAIL],
    )
    log_result("Missing file alert with future date", ok)

# ==================== STRESS TESTS ====================

async def test_rapid_succession():
    """Test sending multiple emails in rapid succession."""
    print("\n[21] Testing rapid succession (5 emails)...")
    results = []
    for i in range(5):
        ok = await email_service.send_email(
            to=[TEST_EMAIL],
            subject=f"Rapid Test #{i+1}",
            body=f"This is rapid test email #{i+1}",
            html=False,
        )
        results.append(ok)
    all_passed = all(results)
    log_result("Rapid succession (5 emails)", all_passed, f"{sum(results)}/5 sent")

async def test_concurrent_emails():
    """Test concurrent email sending."""
    print("\n[22] Testing concurrent emails (5 simultaneous)...")
    tasks = [
        email_service.send_email(
            to=[TEST_EMAIL],
            subject=f"Concurrent Test #{i+1}",
            body=f"This is concurrent test email #{i+1}",
            html=False,
        )
        for i in range(5)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    successful = sum(1 for r in results if r is True)
    log_result("Concurrent emails (5 simultaneous)", successful == 5, f"{successful}/5 sent")

# ==================== EDGE CASE DATES ====================

async def test_leap_year_date():
    """Test with leap year date."""
    print("\n[23] Testing leap year date...")
    leap_date = date(2024, 2, 29)
    ok = await email_service.send_ingestion_failure_alert(
        client_name="Leap Client",
        source="facebook",
        run_date=leap_date,
        error_message="Leap year test",
        admin_emails=[TEST_EMAIL],
    )
    log_result("Leap year date handling", ok)

async def test_year_boundary_date():
    """Test with year boundary date."""
    print("\n[24] Testing year boundary date...")
    boundary_date = date(2024, 12, 31)
    ok = await email_service.send_missing_file_alert(
        client_name="Boundary Client",
        source="vibe",
        expected_date=boundary_date,
        admin_emails=[TEST_EMAIL],
    )
    log_result("Year boundary date handling", ok)

# ==================== HTML RENDERING TESTS ====================

async def test_complex_html():
    """Test complex HTML with tables and styling."""
    print("\n[25] Testing complex HTML...")
    complex_html = """
    <html>
        <head><style>
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; }
            th { background-color: #4CAF50; color: white; }
        </style></head>
        <body>
            <h1>Complex HTML Test</h1>
            <table>
                <tr><th>Column 1</th><th>Column 2</th></tr>
                <tr><td>Data 1</td><td>Data 2</td></tr>
            </table>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
        </body>
    </html>
    """
    ok = await email_service.send_email(
        to=[TEST_EMAIL],
        subject="Complex HTML Test",
        body=complex_html,
        html=True,
    )
    log_result("Complex HTML rendering", ok)

async def test_malformed_html():
    """Test with malformed HTML."""
    print("\n[26] Testing malformed HTML...")
    malformed = "<h1>Unclosed header<p>Unclosed paragraph<div>Unclosed div"
    ok = await email_service.send_email(
        to=[TEST_EMAIL],
        subject="Malformed HTML Test",
        body=malformed,
        html=True,
    )
    log_result("Malformed HTML handling", ok)

# ==================== COMPREHENSIVE TEST RUNNER ====================

async def main():
    global PASSED, FAILED
    print("=" * 80)
    print("COMPREHENSIVE SMTP EMAIL MODULE STRESS TESTS")
    print("=" * 80)
    print(f"Test Email: {TEST_EMAIL}")
    print(f"Start Time: {date.today()}")
    print("=" * 80)

    # Basic Functionality Tests
    print("\n" + "="*80)
    print("SECTION 1: BASIC FUNCTIONALITY TESTS")
    print("="*80)
    await test_basic_email_plain_text()
    await test_basic_email_html()
    await test_multiple_recipients()

    # Edge Cases & Boundary Tests
    print("\n" + "="*80)
    print("SECTION 2: EDGE CASES & BOUNDARY TESTS")
    print("="*80)
    await test_very_long_subject()
    await test_very_long_body()
    await test_special_characters_in_subject()
    await test_unicode_and_emoji()
    await test_html_injection_safety()
    await test_empty_body()
    await test_newlines_and_formatting()

    # Alert-Specific Tests
    print("\n" + "="*80)
    print("SECTION 3: ALERT-SPECIFIC TESTS")
    print("="*80)
    await test_ingestion_failure_alert_normal()
    await test_ingestion_failure_with_long_error()
    await test_ingestion_failure_special_chars()
    await test_validation_error_alert_normal()
    await test_validation_error_many_errors()
    await test_validation_error_empty_list()
    await test_validation_error_special_chars()
    await test_missing_file_alert_normal()
    await test_missing_file_alert_past_date()
    await test_missing_file_alert_future_date()

    # Stress Tests
    print("\n" + "="*80)
    print("SECTION 4: STRESS TESTS")
    print("="*80)
    await test_rapid_succession()
    await test_concurrent_emails()

    # Date Edge Cases
    print("\n" + "="*80)
    print("SECTION 5: DATE EDGE CASES")
    print("="*80)
    await test_leap_year_date()
    await test_year_boundary_date()

    # HTML Rendering Tests
    print("\n" + "="*80)
    print("SECTION 6: HTML RENDERING TESTS")
    print("="*80)
    await test_complex_html()
    await test_malformed_html()

    # Final Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    total = PASSED + FAILED
    pass_rate = (PASSED / total * 100) if total > 0 else 0
    print(f"Total Tests: {total}")
    print(f"Passed: {PASSED} ({pass_rate:.1f}%)")
    print(f"Failed: {FAILED}")
    print("="*80)
    
    if FAILED == 0:
        print("🎉 ALL TESTS PASSED! Email module is robust.")
    else:
        print(f"⚠️  {FAILED} test(s) failed. Review email logs for details.")
    
    print("\n📧 Check your inbox at: " + TEST_EMAIL)
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())