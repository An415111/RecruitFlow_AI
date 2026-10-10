from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    context = browser.new_context()

    page = context.new_page()

    page.goto(
        "https://www.linkedin.com/login"
    )

    print("\nLogin to LinkedIn manually.")

    input(
        "\nAfter LinkedIn Home Feed appears, press Enter..."
    )

    context.storage_state(
        path="linkedin_session.json"
    )

    print(
        "\nSession saved successfully!"
    )

    browser.close()