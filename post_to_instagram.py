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

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # SESSION MANAGEMENT: Try to load existing session
        context_args = {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "viewport": {'width': 1280, 'height': 720}
        }
        
        if SESSION_FILE.exists():
            print("Found existing session. Attempting to resume...")
            context = browser.new_context(storage_state=str(SESSION_FILE), **context_args)
        else:
            print("No session found. Creating fresh context...")
            context = browser.new_context(**context_args)

        page = context.new_page()

        try:
            # 1. Verification of Login State
            print("Navigating to Instagram...")
            page.goto("https://www.instagram.com/", wait_until="networkidle")
            time.sleep(5)
            
            # Check if we are already logged in (look for the "New post" button)
            if not page.locator("svg[aria-label='New post']").is_visible(timeout=5000):
                print("Session expired or invalid. Proceeding to login...")
                page.goto("https://www.instagram.com/accounts/login/", wait_until="networkidle")
                
                # Handle Cookie Consent
                for selector in ['button:has-text("Allow all cookies")', 'button:has-text("Accept")']:
                    try:
                        btn = page.locator(selector)
                        if btn.is_visible(timeout=3000):
                            btn.click()
                            time.sleep(1)
                            break
                    except: continue

                print("Entering credentials...")
                page.locator('input[name="username"]').fill(ACCOUNT_USERNAME)
                page.locator('input[name="password"]').fill(ACCOUNT_PASSWORD)
                page.locator('button[type="submit"]').click()
                
                # Wait for login and SAVE SESSION
                page.wait_for_selector("svg[aria-label='New post']", timeout=45000)
                print("Login successful. Saving session for future use...")
                context.storage_state(path=str(SESSION_FILE))
            else:
                print("Successfully resumed previous session!")

            # 2. Posting Flow
            print("Initiating post creation...")
            page.locator("svg[aria-label='New post']").first.click()
            
            file_chooser_selector = 'input[type="file"]'
            page.wait_for_selector(file_chooser_selector, timeout=10000)
            page.set_input_files(file_chooser_selector, str(image_path.resolve()))
            time.sleep(3)

            # Click Next twice
            next_btn = page.get_by_role("button", name="Next")
            for _ in range(2):
                next_btn.wait_for(state="visible")
                next_btn.click()
                time.sleep(2)

            print("Writing caption...")
            caption_field = page.get_by_label("Write a caption...")
            caption_field.wait_for(state="visible")
            caption_field.fill(caption)

            if alt_text:
                try:
                    page.get_by_text("Accessibility").click()
                    page.get_by_placeholder("Write alt text...").fill(alt_text)
                except: pass

            print("Sharing...")
            page.get_by_role("button", name="Share").click()
            page.wait_for_selector("text=Your post has been shared", timeout=60000)
            print("Post successfully shared!")

        except Exception as e:
            page.screenshot(path=f"{SCREENSHOT_DIR}/error_state.png")
            raise SystemExit(f"Script failed: {e}")
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
    print("Success.")

if __name__ == "__main__":
    main()
