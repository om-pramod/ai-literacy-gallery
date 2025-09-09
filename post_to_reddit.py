import os
import random
import re
import subprocess
import praw
from pathlib import Path
from datetime import datetime, timezone

# --- Configuration ---
CAPTIONS_TO_POST_DIR = Path("captions/to_post")
CAPTIONS_POSTED_DIR = Path("captions/posted")
MEMES_DIR = Path("memes")

# --- Reddit Credentials ---
CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET")
USER_AGENT = os.environ.get("REDDIT_USER_AGENT")
USERNAME = os.environ.get("REDDIT_USERNAME")
PASSWORD = os.environ.get("REDDIT_PASSWORD")
SUBREDDIT_NAME = os.environ.get("SUBREDDIT")

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

def find_matching_image(base_filename: str):
    """Finds a matching image file (.jpg, .png) for a given base filename."""
    for ext in ['.jpg', '.jpeg', '.png']:
        if (image_path := MEMES_DIR / f"{base_filename}{ext}").exists():
            return image_path
    return None

def generate_title_from_filename(filename: str) -> str:
    """Generates a post title from the meme's filename."""
    # Remove extension and replace hyphens/underscores with spaces
    title = re.sub(r'[\-_]', ' ', filename)
    # Capitalize the first letter
    return title.capitalize()

def main():
    """Main execution logic."""
    required_creds = [CLIENT_ID, CLIENT_SECRET, USER_AGENT, USERNAME, PASSWORD, SUBREDDIT_NAME]
    if not all(required_creds):
        raise SystemExit("Error: All Reddit credentials must be set in environment variables.")

    CAPTIONS_TO_POST_DIR.mkdir(exist_ok=True)
    CAPTIONS_POSTED_DIR.mkdir(exist_ok=True)

    md_files = list(CAPTIONS_TO_POST_DIR.glob("*.md"))
    if not md_files:
        raise SystemExit("No captions found in 'captions/to_post'. The queue is empty.")

    random_caption_file = random.choice(md_files)
    base_filename = random_caption_file.stem
    print(f"Selected content: {base_filename}")

    post_title = generate_title_from_filename(base_filename)
    post_body = random_caption_file.read_text()

    image_path = find_matching_image(base_filename)
    if not image_path:
        raise SystemExit(f"Error: No matching image found for caption '{base_filename}'.")
    
    print(f"Found matching image: {image_path}")
    print(f"Generated post title: {post_title}")

    print("Authenticating with Reddit...")
    try:
        reddit = praw.Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            user_agent=USER_AGENT,
            username=USERNAME,
            password=PASSWORD,
        )
        print(f"Authenticated successfully as /u/{reddit.user.me()}")
        subreddit = reddit.subreddit(SUBREDDIT_NAME)
    except Exception as e:
        raise SystemExit(f"An error occurred during Reddit authentication: {e}")

    print(f"Uploading post to r/{SUBREDDIT_NAME}...")
    try:
        submission = subreddit.submit_image(
            title=post_title,
            image_path=str(image_path.resolve())
        )
        # Post the markdown content as the first comment
        submission.reply(post_body)
        print(f"Post published: https://www.reddit.com{submission.permalink}")
    except Exception as e:
        raise SystemExit(f"Failed to submit post to Reddit: {e}")

    print("Updating repository state...")
    setup_git()
    new_caption_path = CAPTIONS_POSTED_DIR / random_caption_file.name
    utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"chore(automation): Post '{base_filename}' to Reddit on {utc_now} UTC"
    run_git_command(["git", "mv", str(random_caption_file), str(new_caption_path)])
    run_git_command(["git", "commit", "-m", commit_message])
    run_git_command(["git", "push"])
    
    print("Repository state updated successfully.")

if __name__ == "__main__":
    main()
