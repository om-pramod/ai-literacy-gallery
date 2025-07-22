import os
import random
import re
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

# --- Configuration ---
CAPTIONS_TO_POST_DIR = Path("captions/to_post")
CAPTIONS_POSTED_DIR = Path("captions/posted")
MEMES_DIR = Path("memes")

# --- Instagram Credentials ---
ACCOUNT_USERNAME = os.environ.get("INSTAGRAM_USERNAME")
ACCOUNT_PASSWORD = os.environ.get("INSTAGRAM_PASSWORD")
SESSION_FILE = Path("session.json")

# --- Git Configuration ---
GIT_USER_NAME = "GitHub Actions Bot"
GIT_USER_EMAIL = "actions@github.com"

def parse_caption_file(filepath: Path):
    """
    Parses the markdown file to extract the main caption, alt text, and hashtags.
    """
    content = filepath.read_text()
    parts = re.split(r"🧐 For those who don't get it:|🧠 Techie Deep Dive:", content)
    main_caption_full = parts[0].strip()
    hashtags = " ".join(re.findall(r"#\w+", main_caption_full))
    main_caption = re.sub(r"#\w+", "", main_caption_full).strip()
    alt_text = parts[1].strip() if len(parts) > 1 else ""
    final_caption = f"{main_caption}\n.\n.\n.\n{hashtags}"
    return final_caption, alt_text

def find_matching_image(base_filename: str):
    """Finds a matching image file (.jpg, .png) for a given base filename."""
    for ext in ['.jpg', '.jpeg', '.png']:
        if (image_path := MEMES_DIR / f"{base_filename}{ext}").exists():
            return image_path
    return None

def run_git_command(command: list):
    """Runs a git command and checks for errors."""
    print(f"Running git command: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing git command: {result.stderr}")
        raise SystemExit(f"Git command failed: {result.stderr}")
    print(result.stdout)

def main():
    """Main execution logic."""
    if not all([ACCOUNT_USERNAME, ACCOUNT_PASSWORD]):
        raise SystemExit("Error: INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD must be set.")

    md_files = list(CAPTIONS_TO_POST_DIR.glob("*.md"))
    if not md_files:
        print("No captions found in 'captions/to_post'. Nothing to post.")
        return

    random_caption_file = random.choice(md_files)
    base_filename = random_caption_file.stem
    print(f"Selected content: {base_filename}")

    caption, alt_text = parse_caption_file(random_caption_file)
    if not (image_path := find_matching_image(base_filename)):
        raise SystemExit(f"Error: No matching image found for caption '{base_filename}'.")
    
    print(f"Found matching image: {image_path}")
    if alt_text: print("Extracted alt text.")

    cl = Client()
    print("Logging in to Instagram...")
    try:
        if SESSION_FILE.exists(): cl.load_settings(SESSION_FILE)
        cl.login(ACCOUNT_USERNAME, ACCOUNT_PASSWORD)
        cl.dump_settings(SESSION_FILE)
        print(f"Logged in successfully as {cl.username}")
    except Exception as e:
        raise SystemExit(f"An error occurred during login: {e}")

    print("Uploading post...")
    try:
        media = cl.photo_upload(path=image_path, caption=caption, extra_data={"accessibility_caption": alt_text})
        print(f"Post published: https://www.instagram.com/p/{media.code}/")
    except Exception as e:
        raise SystemExit(f"Failed to upload post: {e}")

    print("Updating repository state...")
    CAPTIONS_POSTED_DIR.mkdir(exist_ok=True)
    new_caption_path = CAPTIONS_POSTED_DIR / random_caption_file.name
    
    utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"chore(automation): Post '{base_filename}' on {utc_now} UTC"
    
    run_git_command(["git", "config", "user.name", GIT_USER_NAME])
    run_git_command(["git", "config", "user.email", GIT_USER_EMAIL])
    run_git_command(["git", "mv", str(random_caption_file), str(new_caption_path)])
    run_git_command(["git", "commit", "-m", commit_message])
    run_git_command(["git", "push"])
    
    print("Repository state updated successfully.")

if __name__ == "__main__":
    main()
