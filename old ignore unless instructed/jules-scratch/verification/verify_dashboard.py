import re
from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        # Login
        page.goto("http://localhost:5201/login")
        page.get_by_label("Username").fill("admin")
        page.get_by_label("Password").fill("your_admin_password")
        page.get_by_role("button", name="Login").click()

        # Wait for navigation to the main page and for the token to be set
        expect(page).to_have_url("http://localhost:5201/")
        page.wait_for_function("() => localStorage.getItem('access_token')")

        # Go to the dashboard (main page)
        page.goto("http://localhost:5201/")

        # Wait for the year selector to be populated
        expect(page.locator("#year-selector > option")).to_have_count(5, timeout=10000)

        # Select a period that should have mock data
        # The mock data is for the last 2 years, so lets pick a month from last year
        current_year = 2025 # Assuming current year is 2025 for consistency with test
        page.locator("#year-selector").select_option(str(current_year - 1))
        page.locator("#month-selector").select_option("3") # March

        # Click the load button
        page.get_by_role("button", name="Laad Journaal").click()

        # Wait for the financial statement to be visible and have content
        financial_statement_card = page.locator("#financial-statement-card")
        expect(financial_statement_card).to_be_visible(timeout=10000)

        # Check for a specific value in the financial statement
        final_settlement = financial_statement_card.locator(".final-settlement span")
        expect(final_settlement).not_to_be_empty()

        # Take a screenshot
        page.screenshot(path="jules-scratch/verification/verification.png")
        print("Screenshot taken successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        page.screenshot(path="jules-scratch/verification/error.png")
        print("Error screenshot taken.")

    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
