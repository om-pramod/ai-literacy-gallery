import os
import praw

# --- Reddit Credentials ---
CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET")
USER_AGENT = os.environ.get("REDDIT_USER_AGENT")
USERNAME = os.environ.get("REDDIT_USERNAME")
PASSWORD = os.environ.get("REDDIT_PASSWORD")

def main():
    """Deletes the most recent submission on the user's Reddit profile."""
    required_creds = [CLIENT_ID, CLIENT_SECRET, USER_AGENT, USERNAME, PASSWORD]
    if not all(required_creds):
        raise SystemExit("Error: All Reddit credentials must be set in environment variables.")

    print("Connecting to Reddit to delete the last post...")
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

    # Get the user's most recent submission
    print("Fetching the most recent submission...")
    try:
        last_submission = next(redditor.submissions.new(limit=1))
    except StopIteration:
        raise SystemExit("Could not find any submissions on the Reddit account.")

    print(f"Found last post to delete: {last_submission.title} ({last_submission.shortlink})")

    # Delete the post
    print("Deleting post...")
    try:
        last_submission.delete()
        print("✅ Reddit post deleted successfully.")
    except Exception as e:
        print(f"❌ Failed to delete the Reddit post: {e}")

if __name__ == "__main__":
    main()
