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
    print(f"Running git command: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        raise SystemExit(f"Git command failed.")
    print(result.stdout)

def setup_git():
    run_git_command(["git", "config", "user.name", GIT_USER_NAME])
    run_git_command(["git", "config", "user.email", GIT_USER_EMAIL])

def clean_caption_for_instagram(text: str):
    text = re.sub(r'[*_]{1,3}', '', text)
    text = re.sub(r'#+\s', '', text)
    return text.strip()

def parse_caption_file(filepath: Path):
    content = filepath.read_text()
    alt_text = ""
    alt_text_match = re.search(r"🧐 For those who don't get it:(.*?)🧠 Techie Deep Dive:", content, re.DOTALL)
    if alt_text_match:
        alt_text = alt_text_match.group(1).strip()
    return clean_caption_for_instagram(content), alt_text

def find_matching_image(base_filename: str):
    for ext in ['.jpg', '.jpeg', '.png', '.webp']:
        if (image_path := MEMES_DIR / f"{base_filename}{ext}").exists():
            return image_path
    return None

def main():
    if not all([ACCOUNT_USERNAME, ACCOUNT_PASSWORD]):
        raise SystemExit("Error: Credentials missing.")

    SCREENSHOT_DIR.mkdir(exist_ok=True)
    md_files = list(CAPTIONS_TO_POST_DIR.glob("*.md"))
    if not md_files:
        raise SystemExit("Queue is empty.")

    random_caption_file = random.choice(md_files)
    base_filename = random_caption_file.stem
    print(f"Target: {base_filename}")

    caption, alt_text = parse_caption_file(random_caption_file)
    image_path = find_matching_image(base_filename)
    if not image_path:
        raise SystemExit(f"Error: Image missing for {base_filename}")
    
    print(f"Image ready: {image_path}")

    with sync_playwright() as p:
        # Launching with slow_mo to mimic human typing speed
        browser = p.chromium.launch(headless=True, slow_mo=100)
        
        # HIGH-STEALTH CONTEXT
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1440, 'height': 900},
            device_scale_factor=1,
            has_touch=False,
            is_mobile=False,
            locale="en-US",
            timezone_id="UTC"
        )
        
        if SESSION_FILE.exists():
            print("Resuming session...")
            context.add_cookies(eval(SESSION_FILE.read_text()) if SESSION_FILE.stat().st_size > 0 else [])

        page = context.new_page()

        try:
            # 1. AGGRESSIVE NAVIGATION
            print("Opening Instagram...")
            page.goto("https://www.instagram.com/", wait_until="networkidle", timeout=90000)
            time.sleep(10) # Long wait for heavy JS rendering
            
            # Check for empty page
            if not page.title() or "Instagram" not in page.title():
                print("Detected blank page. Attempting refresh...")
                page.reload(wait_until="networkidle")
                time.sleep(10)

            # 2. LOGIN CHECK & EXECUTION
            if not page.locator("svg[aria-label='New post']").is_visible(timeout=15000):
                print("Redirecting to login...")
                page.goto("https://www.instagram.com/accounts/login/", wait_until="domcontentloaded", timeout=90000)
                time.sleep(10)
                
                # Handlers for "Allow Cookies" modals
                for btn_text in ["Allow all cookies", "Allow", "Accept", "Allow essential and optional cookies"]:
                    try:
                        btn = page.get_by_role("button", name=btn_text, exact=False)
                        if btn.is_visible(timeout=5000):
                            print(f"Clicking cookie modal: {btn_text}")
                            btn.click()
                            time.sleep(3)
                    except: continue

                print("Waiting for login form to manifest...")
                # Wait for ANY input to ensure JS is running
                try:
                    page.wait_for_selector("input", timeout=45000)
                except:
                    page.screenshot(path=f"{SCREENSHOT_DIR}/login_stuck.png")
                    print(f"Final URL: {page.url} | Title: {page.title()}")
                    raise SystemExit("Security block: Instagram refused to render the login form.")

                print("Typing credentials...")
                page.get_by_label("Phone number, username, or email").fill(ACCOUNT_USERNAME)
                page.get_by_label("Password").fill(ACCOUNT_PASSWORD)
                page.get_by_role("button", name="Log in", exact=True).click()
                
                # Check for Security Checkpoint
                time.sleep(10)
                if "checkpoint" in page.url:
                    page.screenshot(path=f"{SCREENSHOT_DIR}/checkpoint.png")
                    raise SystemExit("CRITICAL: Instagram triggered a security checkpoint. Open Instagram on your phone and tap 'Yes, it was me'.")

                page.wait_for_selector("svg[aria-label='New post']", timeout=60000)
                print("SUCCESS: Logged in.")
                # Save session state
                storage = context.storage_state(path=str(SESSION_FILE))
            else:
                print("Session active. Skipping login.")

            # 3. ROBUST POSTING
            print("Opening post creator...")
            page.get_by_role("link", name="New post").click()
            time.sleep(5)
            
            print("Uploading image...")
            page.set_input_files('input[type="file"]', str(image_path.resolve()))
            time.sleep(10)

            # Next -> Next
            for _ in range(2):
                page.get_by_role("button", name="Next").click()
                time.sleep(5)

            print("Finalizing caption...")
            page.get_by_label("Write a caption...").fill(caption)

            if alt_text:
                try:
                    page.get_by_role("button", name="Accessibility").click()
                    page.get_by_placeholder("Write alt text...").fill(alt_text)
                except: pass

            print("SHARING...")
            page.get_by_role("button", name="Share").click()
            page.wait_for_selector("text=Your post has been shared", timeout=90000)
            print("🚀 POST IS LIVE!")

        except Exception as e:
            page.screenshot(path=f"{SCREENSHOT_DIR}/last_failure.png")
            print(f"Failure: {e}")
            raise SystemExit("Automation aborted.")
        finally:
            browser.close()

    # 4. REPO UPDATE
    setup_git()
    new_path = CAPTIONS_POSTED_DIR / random_caption_file.name
    utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    run_git_command(["git", "mv", str(random_caption_file), str(new_path)])
    run_git_command(["git", "commit", "-m", f"chore(automation): Post '{base_filename}' at {utc_time} UTC"])
    run_git_command(["git", "push"])
    print("Repository synchronized.")

if __name__ == "__main__":
    main()
