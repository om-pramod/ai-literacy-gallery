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
        # Launching with a specific slow_mo and viewport to be more "human"
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        page = context.new_page()

        try:
            print("Navigating to Instagram login page...")
            page.goto("https://www.instagram.com/accounts/login/", wait_until="networkidle")
            time.sleep(5) # Give it extra time to render
            page.screenshot(path=f"{SCREENSHOT_DIR}/01_login_page_loaded.png")

            # HARDENING: Handle Cookie Consent Dialog (Common cause of failure)
            print("Checking for cookie consent dialog...")
            cookie_buttons = [
                'button:has-text("Allow all cookies")',
                'button:has-text("Allow All Cookies")',
                'button:has-text("Accept All")',
                'button:has-text("Accept")',
                '//button[contains(text(), "Allow")]'
            ]
            for selector in cookie_buttons:
                try:
                    btn = page.locator(selector)
                    if btn.is_visible(timeout=3000):
                        print(f"Found cookie button: {selector}. Clicking...")
                        btn.click()
                        time.sleep(2)
                        break
                except:
                    continue

            print("Entering credentials...")
            # Wait explicitly for the username field with a long timeout
            username_field = page.locator('input[name="username"]')
            username_field.wait_for(state="visible", timeout=30000)
            username_field.fill(ACCOUNT_USERNAME)
            
            password_field = page.locator('input[name="password"]')
            password_field.fill(ACCOUNT_PASSWORD)
            
            page.screenshot(path=f"{SCREENSHOT_DIR}/02_credentials_entered.png")

            print("Clicking login button...")
            page.locator('button[type="submit"]').click()

            print("Waiting for login to complete...")
            # Increased timeout and multi-selector wait
            try:
                page.wait_for_selector("svg[aria-label='New post'], text=Save your login info?, main", timeout=45000)
            except PlaywrightTimeoutError:
                print("Login wait timed out. Checking for security checks...")
                page.screenshot(path=f"{SCREENSHOT_DIR}/error_login_timeout.png")
                # Check for "Suspicious Login Attempt" or similar
                if "checkpoint" in page.url:
                    raise SystemExit("Error: Instagram triggered a security checkpoint. Manual intervention required.")
                raise

            page.screenshot(path=f"{SCREENSHOT_DIR}/03_post_login_state.png")

            # Handle "Save Info" dialog if it appears
            save_info_button = page.get_by_role("button", name="Save Info").or_(page.get_by_role("button", name="Not Now"))
            if save_info_button.first.is_visible(timeout=5000):
                print("Handling 'Save Info' or 'Not Now' dialog...")
                save_info_button.first.click()
                time.sleep(2)

            # Handle "Turn on Notifications" dialog if it appears
            not_now_button = page.get_by_role("button", name="Not Now")
            if not_now_button.is_visible(timeout=5000):
                print("Handling 'Turn on Notifications' dialog...")
                not_now_button.click()
                time.sleep(2)

            print("Login successful. Navigating to create post...")
            create_button = page.locator("svg[aria-label='New post']").first
            create_button.wait_for(state="visible", timeout=10000)
            create_button.click()

            print("Selecting image file...")
            file_chooser_selector = 'input[type="file"]'
            page.wait_for_selector(file_chooser_selector, timeout=10000)
            page.set_input_files(file_chooser_selector, str(image_path.resolve()))
            time.sleep(3)

            print("Navigating through post creation flow...")
            # Use more robust "Next" button detection
            next_button = page.get_by_role("button", name="Next")
            next_button.wait_for(state="visible")
            next_button.click()
            time.sleep(2)
            
            next_button.wait_for(state="visible")
            next_button.click()
            time.sleep(2)

            print("Writing caption and alt text...")
            caption_field = page.get_by_label("Write a caption...")
            caption_field.wait_for(state="visible")
            caption_field.fill(caption)

            if alt_text:
                try:
                    page.get_by_text("Accessibility").click()
                    page.get_by_placeholder("Write alt text...").fill(alt_text)
                    print("Alt text entered successfully.")
                except:
                    print("Could not find Accessibility settings, skipping alt-text.")

            print("Sharing post...")
            share_button = page.get_by_role("button", name="Share")
            share_button.click()

            # Wait for the "Post shared" confirmation
            print("Waiting for share confirmation...")
            page.wait_for_selector("text=Your post has been shared", timeout=60000)
            print("Post successfully shared!")

        except PlaywrightTimeoutError as e:
            print(f"A timeout error occurred: {e}")
            page.screenshot(path=f"{SCREENSHOT_DIR}/error_timeout.png")
            raise SystemExit(f"Script failed due to timeout. Screenshot saved to {SCREENSHOT_DIR}/error_timeout.png")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            page.screenshot(path=f"{SCREENSHOT_DIR}/error_unexpected.png")
            raise SystemExit(f"Script failed unexpectedly: {e}")
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
