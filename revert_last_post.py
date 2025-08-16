import os
import re
import subprocess
import praw
from pathlib import Path

# --- Configuration ---
CAPTIONS_TO_POST_DIR = Path("captions/to_post")
CAPTIONS_POSTED_DIR = Path("captions/posted")
GIT_BOT_AUTHOR = "GitHub Actions Bot"
GIT_USER_NAME = "GitHub Actions Bot"
GIT_USER_EMAIL = "actions@github.com"

# --- Reddit Credentials ---
CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET")
USER_AGENT = os.environ.get("REDDIT_USER_AGENT")
USERNAME = os.environ.get("REDDIT_USERNAME")
PASSWORD = os.environ.get("REDDIT_PASSWORD")

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
        if e.returncode == 1 and not e.stdout and not e.stderr:
            return ""
        print(f"Error running command:\n{e.stderr}")
        raise SystemExit(f"Command failed: {e.stderr}")

def main():
    """Main execution logic to revert the last post."""
    required_creds = [CLIENT_ID, CLIENT_SECRET, USER_AGENT, USERNAME, PASSWORD]
    if not all(required_creds):
        raise SystemExit("Error: All Reddit credentials must be set in environment variables.")

    # --- 1. Revert on GitHub ---
    print("Step 1: Reverting the last post on GitHub...")
    run_command(["git", "config", "user.name", GIT_USER_NAME])
    run_command(["git", "config", "user.email", GIT_USER_EMAIL])
    
    last_post_commit_msg = run_command([
        "git", "log", f"--author={GIT_BOT_AUTHOR}", "--grep=^chore(automation): Post", "--pretty=format:%s", "-n", "1"
    ])
    
    if not last_post_commit_msg:
        raise SystemExit("Could not find any post commits made by the bot to revert.")
    
    print(f"Found last post commit to revert: '{last_post_commit_msg}'")
    
    # Updated regex for the new commit message format
    match = re.search(r"Post '(.*?)' to Reddit", last_post_commit_msg)
    if not match:
        raise SystemExit(f"Could not parse filename from the commit message: '{last_post_commit_msg}'")
        
    base_filename = match.group(1)
    
    posted_file = CAPTIONS_POSTED_DIR / f"{base_filename}.md"
    if not posted_file.exists():
        raise SystemExit(f"Error: '{posted_file}' is not in the posted folder. Has it already been reverted?")

    to_post_path = CAPTIONS_TO_POST_DIR / posted_file.name
    run_command(["git", "mv", str(posted_file), str(to_post_path)])
    
    commit_message = f"revert: Move '{base_filename}' back to to_post queue"
    run_command(["git", "commit", "-m", commit_message])
    print("Pushing the revert commit to GitHub...")
    run_command(["git", "push"])
    print("✅ GitHub revert successful.")

    # --- 2. Delete on Reddit ---
    print("\nStep 2: Deleting the post on Reddit...")
    try:
        reddit = praw.Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            user_agent=USER_AGENT,
            username=USERNAME,
            password=PASSWORD,
        )
        redditor = reddit.user.me()
        print(f"Authenticated successfully as /u/{redditor.name}")
    except Exception as e:
        raise SystemExit(f"An error occurred during Reddit authentication: {e}")

    print("Fetching the most recent submission...")
    try:
        last_submission = next(redditor.submissions.new(limit=1))
    except StopIteration:
        raise SystemExit("Could not find any submissions on the Reddit account to delete.")
        
    print(f"Found last post to delete: {last_submission.title} ({last_submission.shortlink})")
    
    print("Deleting post...")
    try:
        last_submission.delete()
        print("✅ Reddit post deleted successfully.")
    except Exception as e:
        print(f"❌ Failed to delete the Reddit post: {e}")

if __name__ == "__main__":
    main()
