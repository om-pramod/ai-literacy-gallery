import os
from pathlib import Path
from instagrapi import Client

# --- Instagram Credentials ---
ACCOUNT_USERNAME = os.environ.get("INSTAGRAM_USERNAME")
ACCOUNT_PASSWORD = os.environ.get("INSTAGRAM_PASSWORD")
SESSION_FILE = Path("session.json")

def main():
    """Archives the last media post on Instagram."""
    if not all([ACCOUNT_USERNAME, ACCOUNT_PASSWORD]):
        raise SystemExit("Error: INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD secrets must be set.")

    print("Connecting to Instagram to archive the last post...")
    cl = Client()
    
    try:
        print("Logging in to Instagram...")
        if SESSION_FILE.exists():
            cl.load_settings(SESSION_FILE)
        cl.login(ACCOUNT_USERNAME, ACCOUNT_PASSWORD)
        cl.dump_settings(SESSION_FILE)
    except Exception as e:
        raise SystemExit(f"An error occurred during Instagram login: {e}")

    # Get the user's most recent post
    print("Fetching the most recent media post...")
    user_id = cl.user_id_from_username(ACCOUNT_USERNAME)
    medias = cl.user_medias(user_id, amount=1)
    
    if not medias:
        raise SystemExit("Could not find any media on the Instagram account.")
        
    last_media = medias[0]
    print(f"Found last post to archive: https://www.instagram.com/p/{last_media.code}/")
    
    # Archive the post
    print("Archiving post...")
    if cl.media_archive(last_media.pk):
        print("✅ Instagram post archived successfully.")
    else:
        print("❌ Failed to archive the Instagram post.")

if __name__ == "__main__":
    main()