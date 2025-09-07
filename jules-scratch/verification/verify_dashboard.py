from playwright.sync_api import sync_playwright, expect

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # 1. Navigate to the application
            page.goto("http://localhost:5201", timeout=30000)

            # 2. Wait for the dashboard to load data and render
            # We'll wait for the ROI tracker to have some content and a chart canvas to be present.
            # This indicates that the async data loading has finished.
            roi_tracker_locator = page.locator("#roi-tracker .progress-bar")
            energy_chart_locator = page.locator("canvas#energyBalanceChart")

            # With an empty database, we expect the main charts to render with 0 values,
            # and the ROI tracker to show a "not available" message.
            # So, we assert that this specific text is visible.
            expect(page.get_by_text("ROI data not available.")).to_be_visible(timeout=15000)
            expect(energy_chart_locator).to_be_visible(timeout=15000)

            # Optional: Add a small delay to ensure charts have finished their animations
            page.wait_for_timeout(1000)

            # 3. Take a screenshot
            screenshot_path = "jules-scratch/verification/verification.png"
            page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")

        except Exception as e:
            print(f"An error occurred during verification: {e}")
            # In case of error, take a screenshot of the current state for debugging
            page.screenshot(path="jules-scratch/verification/error.png")
            print("Error screenshot saved to jules-scratch/verification/error.png")

        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()
