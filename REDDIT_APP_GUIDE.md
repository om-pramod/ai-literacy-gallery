# How to Get Reddit API Credentials for Your Bot

To run this bot, you need to give it permission to post on your behalf. You can do this by creating a "script" application on Reddit. Follow these steps to get the necessary credentials.

## Step 1: Go to Reddit's App Preferences

1.  Make sure you are logged into the Reddit account you want to post from.
2.  Navigate to this URL: [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)

## Step 2: Create a New Application

1.  Scroll down to the bottom of the page and click the **"are you a developer? create an app..."** button.
2.  Fill out the application form:
    *   **name:** Give your app a descriptive name, like `my-meme-poster-bot`.
    *   **app icon:** You can leave this blank.
    *   **app description:** You can leave this blank.
    *   **about url:** You can leave this blank.
    *   Select the **"script"** app type. This is very important. It's for personal automation scripts like this one.
    *   **redirect uri:** This is not needed for script apps, but you must enter a valid URL. Use `http://localhost:8080`.

3.  Click the **"create app"** button.

## Step 3: Find Your Credentials

1.  After creating the app, you will see it listed on the "apps" page.
2.  Your app's name will be displayed, and underneath it, you will find your **personal use script** client ID. This is your `CLIENT_ID`.
    *   It's the string of letters and numbers right below the app name.
3.  Next to that, you will see the word **"secret"**. This is your `CLIENT_SECRET`.

## Step 4: Understand Your User Agent

A User Agent is a unique identifier for your bot. It helps Reddit know who is using their API. A good user agent is descriptive and includes your username. It prevents your bot from being blocked.

**You do not need to "find" this value. You create it yourself.**

A good format is: `<platform>:<app_name>:<version> (by /u/<your_reddit_username>)`

**Example:** `python:my-meme-poster-bot:v1.0 (by /u/your_username_here)`

You will use this string for the `REDDIT_USER_AGENT` secret.

## Step 5: Configure Your Bot's Secrets

Once you have all the pieces of information, you need to add them as secrets to your GitHub repository so the bot can use them.

1.  **`REDDIT_CLIENT_ID`**: The "personal use script" value from Step 3.
2.  **`REDDIT_CLIENT_SECRET`**: The "secret" value from Step 3.
3.  **`REDDIT_USER_AGENT`**: The descriptive string you created in Step 4.
4.  **`REDDIT_USERNAME`**: The Reddit username you are posting from.
5.  **`REDDIT_PASSWORD`**: The password for that Reddit account.
6.  **`SUBREDDIT`**: The name of the subreddit you want to post to (without the `r/` prefix, e.g., `MyMemeSub`).

That's it! Once these secrets are configured, the bot will be able to authenticate with Reddit and post on your behalf.
