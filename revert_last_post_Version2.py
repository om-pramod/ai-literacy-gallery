import os
import re
import subprocess
from pathlib import Path
from instagrapi import Client

# --- Configuration ---
CAPTIONS_TO_POST_DIR = Path("captions/to_post")
CAPTIONS_POSTED_DIR = Path("captions/posted")
GIT_BOT_AUTHOR = "GitHub Actions Bot"
GIT_USER_NAME = "GitHub Actions Bot"
GIT_USER_EMAIL = "actions@github.com"

# --- Instagram Credentials ---
ACCOUNT_USERNAME = os.environ.get("INSTAGRAM_USERNAME")
ACCOUNT_PASSWORD = os.environ.get("INSTAGRAM_PASSWORD")
SESSION_FILE = Path("session.json")

def run_command(command: list):
    """Runs a shell command and returns its output."""
    print(f"Running command: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        print(result.stdout)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command:\n{e.stderr}")
        raise SystemExit(f"Command failed: {e.stderr}")

def main():
    """Main execution logic to revert the last post."""
    if not all([ACCOUNT_USERNAME, ACCOUNT_PASSWORD]):
        raise SystemExit("Error: INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD secrets must be set.")

    # --- 1. Revert on GitHub ---
    print("Step 1: Reverting the last commit on GitHub...")
    run_command(["git", "config", "user.name", GIT_USER_NAME])
    run_command(["git", "config", "user.email", GIT_USER_EMAIL])
    
    last_commit_msg = run_command(["git", "log", f"--author={GIT_BOT_AUTHOR}", "--pretty=format:%s", "-n", "1"])
    if not last_commit_msg:
        raise SystemExit("Could not find any posts made by the GitHub Actions Bot.")
    
    print(f"Found last post commit: '{last_commit_msg}'")
    
    match = re.search(r"Post '(.*?)'", last_commit_msg)
    if not match:
        raise SystemExit("Could not parse the filename from the commit message.")
        
    base_filename = match.group(1)
    
    posted_file = CAPTIONS_POSTED_DIR / f"{base_filename}.md"
    if not posted_file.exists():
        raise SystemExit(f"Error: Could not find '{posted_file}'. Already reverted?")

    to_post_path = CAPTIONS_TO_POST_DIR / posted_file.name
    run_command(["git", "mv", str(posted_file), str(to_post_path)])
    
    commit_message = f"revert: Move '{base_filename}' back to to_post queue"
    run_command(["git", "commit", "-m", commit_message])
    print("Pushing the revert commit to GitHub...")
    run_command(["git", "push"])
    print("✅ GitHub revert successful.")

    # --- 2. Archive on Instagram ---
    print("\nStep 2: Archiving the post on Instagram...")
    cl = Client()
    
    try:
        print("Logging in to Instagram...")
        if SESSION_FILE.exists(): cl.load_settings(SESSION_FILE)
        cl.login(ACCOUNT_USERNAME, ACCOUNT_PASSWORD)
        cl.dump_settings(SESSION_FILE)
    except Exception as e:
        raise SystemExit(f"An error occurred during Instagram login: {e}")

    user_id = cl.user_id_from_username(ACCOUNT_USERNAME)
    medias = cl.user_medias(user_id, amount=1)
    
    if not medias:
        raise SystemExit("Could not find any media on the Instagram account.")
        
    last_media = medias[0]
    print(f"Found last post: https://www.instagram.com/p/{last_media.code}/")
    
    print("Archiving post...")
    if cl.media_archive(last_media.pk):
        print("✅ Instagram post archived successfully.")
    else:
        print("❌ Failed to archive the Instagram post.")

if __name__ == "__main__":
    main()