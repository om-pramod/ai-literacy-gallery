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
SESSION_FILE = Path("session.json")

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
    content = filepath.read_text()
    alt_text = ""
    alt_text_match = re.search(r"🧐 For those who don't get it:(.*?)🧠 Techie Deep Dive:", content, re.DOTALL)
    if alt_text_match:
        alt_text = alt_text_match.group(1).strip()
    return content.strip(), alt_text

def find_matching_image(base_filename: str):
    for ext in ['.jpg', '.jpeg', '.png']:
        if (image_path := MEMES_DIR / f"{base_filename}{ext}").exists():
            return image_path
    return None

def main():
    if not all([ACCOUNT_USERNAME, ACCOUNT_PASSWORD]):
        raise SystemExit("Error: INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD must be set.")

    SCREENSHOT_DIR.mkdir(exist_ok=True)
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

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # Use a very common user agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        
        if SESSION_FILE.exists():
            print("Found existing session. Attempting to resume...")
            context = browser.new_context(storage_state=str(SESSION_FILE), user_agent=user_agent, viewport={'width': 1280, 'height': 720})
        else:
            print("No session found. Creating fresh context...")
            context = browser.new_context(user_agent=user_agent, viewport={'width': 1280, 'height': 720})

        page = context.new_page()

        try:
            print("Navigating to Instagram...")
            page.goto("https://www.instagram.com/", wait_until="networkidle", timeout=60000)
            time.sleep(5)
            
            # Check for login
            if not page.locator("svg[aria-label='New post']").is_visible(timeout=10000):
                print("Not logged in or session expired. Heading to login page...")
                page.goto("https://www.instagram.com/accounts/login/", wait_until="networkidle", timeout=60000)
                time.sleep(5)
                page.screenshot(path=f"{SCREENSHOT_DIR}/login_page_loaded.png")
                
                # Handle cookie consent
                cookie_selectors = ['button:has-text("Allow all cookies")', 'button:has-text("Accept")', 'button:has-text("Allow")']
                for sel in cookie_selectors:
                    try:
                        if page.locator(sel).is_visible(timeout=5000):
                            print(f"Clicking cookie button: {sel}")
                            page.locator(sel).click()
                            time.sleep(2)
                            break
                    except: continue

                print("Searching for login fields...")
                # Robust login field detection
                username_selectors = [
                    'input[name="username"]',
                    'input[aria-label*="Phone number"]',
                    'input[placeholder*="username"]',
                    '//input[@name="username"]'
                ]
                
                username_field = None
                for sel in username_selectors:
                    try:
                        field = page.locator(sel)
                        if field.is_visible(timeout=5000):
                            username_field = field
                            print(f"Found username field with: {sel}")
                            break
                    except: continue

                if not username_field:
                    page.screenshot(path=f"{SCREENSHOT_DIR}/login_failure_context.png")
                    print(f"Current URL: {page.url}")
                    print(f"Page Title: {page.title()}")
                    raise SystemExit("Could not find username field. Instagram might be blocking this runner.")

                print("Entering credentials...")
                username_field.fill(ACCOUNT_USERNAME)
                page.locator('input[name="password"]').fill(ACCOUNT_PASSWORD)
                page.locator('button[type="submit"]').click()
                
                print("Waiting for login confirmation...")
                page.wait_for_selector("svg[aria-label='New post'], text=Save your login info?", timeout=60000)
                print("Login successful. Saving session...")
                context.storage_state(path=str(SESSION_FILE))
            else:
                print("Already logged in via session!")

            # Posting Logic
            print("Creating new post...")
            page.locator("svg[aria-label='New post']").first.click()
            time.sleep(2)
            
            page.set_input_files('input[type="file"]', str(image_path.resolve()))
            time.sleep(5)

            # Navigation
            for _ in range(2):
                next_btn = page.get_by_role("button", name="Next")
                next_btn.wait_for(state="visible", timeout=15000)
                next_btn.click()
                time.sleep(2)

            print("Entering caption...")
            caption_box = page.get_by_label("Write a caption...")
            caption_box.wait_for(state="visible")
            caption_box.fill(caption)

            if alt_text:
                try:
                    print("Opening Advanced Settings for Alt-Text...")
                    # Instagram often hides Accessibility under "Advanced settings"
                    adv_btn = page.get_by_role("button", name="Advanced settings")
                    if adv_btn.is_visible():
                        adv_btn.click()
                        time.sleep(1)
                    
                    page.get_by_text("Write alt text").first.click()
                    page.get_by_placeholder("Write alt text...").fill(alt_text)
                    print("Alt-text applied successfully.")
                except:
                    print("Could not navigate to Alt-text settings, sharing without it.")

            print("Sharing...")
            page.get_by_role("button", name="Share").click()
            page.wait_for_selector("text=Your post has been shared", timeout=90000)
            print("SUCCESS: Post shared to Instagram!")

        except Exception as e:
            page.screenshot(path=f"{SCREENSHOT_DIR}/error_state.png")
            print(f"An error occurred: {e}")
            raise SystemExit(f"Automation failed.")
        finally:
            browser.close()

    print("Updating Git repository...")
    setup_git()
    new_caption_path = CAPTIONS_POSTED_DIR / random_caption_file.name
    utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    run_git_command(["git", "mv", str(random_caption_file), str(new_caption_path)])
    run_git_command(["git", "commit", "-m", f"chore(automation): Post '{base_filename}' on {utc_now} UTC"])
    run_git_command(["git", "push"])
    print("Done.")

if __name__ == "__main__":
    main()
