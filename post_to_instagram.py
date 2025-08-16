import os
import random
import re
import subprocess
import time
from pathlib import Path
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# --- Configuration ---
CAPTIONS_TO_POST_DIR = Path("captions/to_post")
CAPTIONS_POSTED_DIR = Path("captions/posted")
MEMES_DIR = Path("memes")
SCREENSHOT_DIR = Path("screenshots")

# --- Instagram Credentials ---
ACCOUNT_USERNAME = os.environ.get("INSTAGRAM_USERNAME")
ACCOUNT_PASSWORD = os.environ.get("INSTAGRAM_PASSWORD")

# --- Git Configuration ---
GIT_USER_NAME = "GitHub Actions Bot"
GIT_USER_EMAIL = "actions@github.com"

def run_git_command(command: list):
    """Runs a git command and checks for errors."""
    print(f"Running git command: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing git command: {result.stderr}")
        raise SystemExit(f"Git command failed: {result.stderr}")
    print(result.stdout)

def setup_git():
    """Configures git user name and email."""
    run_git_command(["git", "config", "user.name", GIT_USER_NAME])
    run_git_command(["git", "config", "user.email", GIT_USER_EMAIL])

def parse_caption_file(filepath: Path):
    """
    Uses the ENTIRE file content for the caption, while still
    extracting the alt text for accessibility.
    """
    content = filepath.read_text()
    alt_text = ""
    alt_text_match = re.search(r"🧐 For those who don't get it:(.*?)🧠 Techie Deep Dive:", content, re.DOTALL)
    if alt_text_match:
        alt_text = alt_text_match.group(1).strip()
    return content.strip(), alt_text

def find_matching_image(base_filename: str):
    """Finds a matching image file (.jpg, .png) for a given base filename."""
    for ext in ['.jpg', '.jpeg', '.png']:
        if (image_path := MEMES_DIR / f"{base_filename}{ext}").exists():
            return image_path
    return None

def main():
    """Main execution logic."""
    if not all([ACCOUNT_USERNAME, ACCOUNT_PASSWORD]):
        raise SystemExit("Error: INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD must be set.")

    SCREENSHOT_DIR.mkdir(exist_ok=True)
    CAPTIONS_TO_POST_DIR.mkdir(exist_ok=True)
    CAPTIONS_POSTED_DIR.mkdir(exist_ok=True)

    md_files = list(CAPTIONS_TO_POST_DIR.glob("*.md"))
    if not md_files:
        raise SystemExit("No captions found in 'captions/to_post'. The queue is empty.")

    random_caption_file = random.choice(md_files)
    base_filename = random_caption_file.stem
    print(f"Selected content: {base_filename}")

    caption, alt_text = parse_caption_file(random_caption_file)
    image_path = find_matching_image(base_filename)
    if not image_path:
        raise SystemExit(f"Error: No matching image found for caption '{base_filename}'.")
    
    print(f"Found matching image: {image_path}")
    if alt_text:
        print("Extracted alt text for accessibility.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
        page = context.new_page()

        try:
            print("Navigating to Instagram login page...")
            page.goto("https://www.instagram.com/accounts/login/")
            page.screenshot(path=f"{SCREENSHOT_DIR}/01_login_page.png")

            print("Entering credentials...")
            page.locator('input[name="username"]').fill(ACCOUNT_USERNAME)
            page.locator('input[name="password"]').fill(ACCOUNT_PASSWORD)
            page.screenshot(path=f"{SCREENSHOT_DIR}/02_credentials_entered.png")

            print("Clicking login button...")
            page.locator('button[type="submit"]').click()

            print("Waiting for login to complete...")
            # Wait for either a "Save your login info?" dialog or the main page content
            page.wait_for_selector("text=Save your login info? , main", timeout=15000)
            page.screenshot(path=f"{SCREENSHOT_DIR}/03_post_login.png")

            # Handle "Save Info" dialog if it appears
            save_info_button = page.locator('text=Save Info').or_(page.locator('text=Save info'))
            if save_info_button.is_visible():
                print("Handling 'Save Info' dialog...")
                save_info_button.click()
                page.screenshot(path=f"{SCREENSHOT_DIR}/04_save_info_dialog.png")

            # Handle "Turn on Notifications" dialog if it appears
            not_now_button = page.locator('text=Not Now')
            if not_now_button.is_visible():
                print("Handling 'Turn on Notifications' dialog...")
                not_now_button.click()
                page.screenshot(path=f"{SCREENSHOT_DIR}/05_notifications_dialog.png")

            print("Login successful. Navigating to create post...")
            # Use the SVG path to find the "New post" button
            create_button_selector = "svg[aria-label='New post']"
            page.wait_for_selector(create_button_selector, timeout=10000)
            page.locator(create_button_selector).first.click()

            print("Selecting image file...")
            page.screenshot(path=f"{SCREENSHOT_DIR}/06_create_post_dialog.png")

            # The file chooser is triggered by the button inside the dialog
            file_chooser_selector = 'input[type="file"]'
            page.wait_for_selector(file_chooser_selector)
            page.set_input_files(file_chooser_selector, str(image_path.resolve()))
            page.screenshot(path=f"{SCREENSHOT_DIR}/07_file_selected.png")

            print("Navigating through post creation flow...")
            # Click "Next"
            page.locator('div[role="dialog"] button:has-text("Next")').click()
            page.screenshot(path=f"{SCREENSHOT_DIR}/08_filters_screen.png")

            # Click "Next" again (skipping filters)
            page.locator('div[role="dialog"] button:has-text("Next")').click()
            page.screenshot(path=f"{SCREENSHOT_DIR}/09_caption_screen.png")

            print("Writing caption and alt text...")
            page.locator('div[aria-label="Write a caption..."]').fill(caption)

            if alt_text:
                page.locator('text=Accessibility').click()
                page.locator('textarea[placeholder="Write alt text..."]').fill(alt_text)
                page.screenshot(path=f"{SCREENSHOT_DIR}/10_alt_text_entered.png")

            print("Sharing post...")
            page.locator('div[role="dialog"] button:has-text("Share")').click()

            # Wait for the "Post shared" confirmation
            page.wait_for_selector("text=Post shared", timeout=30000)
            page.screenshot(path=f"{SCREENSHOT_DIR}/11_post_shared.png")
            print("Post successfully shared!")

        except PlaywrightTimeoutError as e:
            print(f"A timeout error occurred: {e}")
            page.screenshot(path=f"{SCREENSHOT_DIR}/error.png")
            raise SystemExit(f"Script failed due to timeout. See error.png for details.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            page.screenshot(path=f"{SCREENSHOT_DIR}/error.png")
            raise SystemExit(f"Script failed unexpectedly. See error.png for details.")
        finally:
            browser.close()

    print("Updating repository state...")
    setup_git()
    new_caption_path = CAPTIONS_POSTED_DIR / random_caption_file.name
    utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"chore(automation): Post '{base_filename}' on {utc_now} UTC"
    run_git_command(["git", "mv", str(random_caption_file), str(new_caption_path)])
    run_git_command(["git", "commit", "-m", commit_message])
    run_git_command(["git", "push"])
    
    print("Repository state updated successfully.")

if __name__ == "__main__":
    main()
