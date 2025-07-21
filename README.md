# Instagram Automation Project

This project automates the process of posting AI and tech-related memes to Instagram, complete with intelligent captioning, image handling, and robust error management. The entire system runs serverlessly using GitHub Actions, eliminating the need for a continuously running local server.

## 🚀 Project Goal

The primary goal is to create a "set it and forget it" system for consistent Instagram content delivery, focusing on:
*   **Automation:** Posting memes on a predefined schedule.
*   **Variety:** Randomly selecting content to keep the feed fresh.
*   **Intelligence:** Generating meaningful captions and alt text.
*   **Reliability:** Ensuring the system runs autonomously and notifies of issues.
*   **Scalability:** Operating entirely in the cloud without local dependencies.

## 📂 Repository Structure

The repository is organized to clearly separate content from automation logic.

```
instagram-automation/
├── .github/
│   └── workflows/
│       └── scheduler.yml           # GitHub Actions workflow for scheduling and execution
├── .n8n/
│   └── workflows/
│       └── publisher_workflow.json # n8n workflow definition (the core logic)
├── captions/
│   ├── posted/                     # Stores markdown captions that have already been posted
│   └── to_post/                    # Stores markdown captions ready to be posted
│       ├── meme_1.md
│       ├── AI cloud cost optimization backfire.md
│       └── ...
├── memes/                          # Stores image files (JPG, PNG) corresponding to captions
│   ├── meme_1.jpg
│   ├── AI cloud cost optimization backfire.png
│   └── ...
└── README.md                       # This project documentation
```

## 📝 Content Explanation

### Captions (`captions/to_post/` and `captions/posted/`)
These are Markdown (`.md`) files containing the text for your Instagram posts. Each file is structured to provide:
*   The main caption text.
*   A "For those who don't get it" section (used for intelligent alt text).
*   A "Techie Deep Dive" section (for additional context).
*   Relevant hashtags.

**Example Content Structure (inside a `.md` file):**
```markdown
The main caption text goes here. It's usually short and punchy.

.
.
.

🧐 For those who don't get it:
This section explains the meme or concept in simple terms. This content is extracted and used as the image's alt text.

.
.
.

🧠 Techie Deep Dive:
This section provides more technical context or explanation for the meme.

.
.
.

#Hashtag1 #Hashtag2 #TechMemes #AIHumor
```

### Memes (`memes/`)
This directory holds the image files (JPG or PNG) that correspond to your captions. The filename of the image **must match the filename of its corresponding Markdown caption file** (excluding the extension).
*   `meme_1.md` corresponds to `meme_1.jpg` or `meme_1.png`.
*   `AI cloud cost optimization backfire.md` corresponds to `AI cloud cost optimization backfire.png`.

## 💡 Evolution of the Architecture & Strategy

The project evolved through several stages to achieve its current robust and serverless state.

### Phase 1: Initial Local Setup (Proposed)
*   **Concept:** Use GitHub Actions to trigger a webhook, which would then activate a locally running n8n Docker container.
*   **Limitations:** This approach created a fragile dependency on the user's local machine (Docker had to be running 24/7, internet connection stable, etc.). If the local environment failed, the automation stopped.

### Phase 2: Fully Serverless with GitHub Actions (Current Implementation)
*   **Concept:** The entire n8n workflow executes directly within GitHub Actions. GitHub Actions spins up a temporary n8n Docker container, runs the workflow, and then tears it down.
*   **Benefits:**
    *   **No Local Dependency:** No need for a local Docker instance or server.
    *   **High Reliability:** GitHub Actions handles the execution environment, retries, and scaling.
    *   **Cost-Effective:** Resources are only consumed during the brief execution window.
    *   **Secure:** Secrets are managed by GitHub, not exposed in code or local files.

## ✨ Key Features & Execution Strategies

### 1. Automated Scheduling
*   **Mechanism:** The `.github/workflows/scheduler.yml` file defines a `cron` schedule (`0 9,17 * * *`) to trigger the workflow twice daily (9 AM and 5 PM UTC). It can also be triggered manually via `workflow_dispatch`.

### 2. Content Synchronization
*   **Mechanism:** The n8n workflow starts with a `git pull` command (`Execute Command (Git Pull)` node) to ensure the GitHub Actions runner has the latest `captions` and `memes` from the repository.

### 3. Random Content Selection
*   **Mechanism:** The `List Files` node retrieves all `.md` files from `captions/to_post/`. A `Function (Select Random Caption)` node then randomly selects one file from this list, ensuring variety in posts.

### 4. Dynamic Image Matching
*   **Mechanism:** After selecting a caption, the workflow extracts its base filename. The `Find Matching Meme File` node then searches the `memes/` directory for an image with the same base name, regardless of whether its extension is `.jpg` or `.png`. This prevents failures due to mismatched image formats.

### 5. Automated Instagram Posting
*   **Mechanism:** The `Instagram Post` node uses the extracted caption content and the dynamically found image to publish the post to Instagram.

### 6. Robust State Management
*   **Mechanism:** After a successful post, the `Execute Command (Git Move & Commit)` node moves the posted Markdown file from `captions/to_post/` to `captions/posted/` and commits this change back to the GitHub repository. This ensures content is not re-posted and maintains a history of published memes.

### 7. Secure Credential Handling
*   **Mechanism:** All sensitive credentials (Instagram username/password, SMTP details, n8n encryption key) are stored as GitHub Secrets. These are securely injected as environment variables into the n8n Docker container only during workflow execution.

### 8. Enhanced Error Handling & Notifications
*   **Informative Failure Alerts:** If any node within the n8n workflow fails, a `Send Failure Email` node is triggered. This email includes the specific node name and the exact error message, allowing for quick diagnosis.
*   **Low Content Warning:** The workflow includes an `IF (Content Low?)` node that checks the number of remaining captions in `captions/to_post/`. If the count falls below a threshold (e.g., 5), a `Send Low Content Warning Email` is sent, prompting the user to add more content before the supply runs out.

### 9. Intelligent Alt Text Generation
*   **Mechanism:** The `Extract Alt Text` function node parses the selected Markdown caption. It specifically extracts the content from the "🧐 For those who don't get it:" section. This extracted text is then truncated to a maximum of 250 characters (with "...") to meet Instagram's best practices for alt text length.
*   **Benefit:** Improves accessibility for visually impaired users and enhances the discoverability of posts on Instagram.

## 🛠️ Setup Instructions (for a new user)

To get this automation running in a new repository:

1.  **Clone the Repository:** `git clone [your-repo-url]`
2.  **Add Content:** Place your Markdown captions in `captions/to_post/` and corresponding images in `memes/`.
3.  **Add GitHub Secrets:** Go to your GitHub repository's `Settings > Secrets and variables > Actions` and add the following secrets:
    *   `N8N_ENCRYPTION_KEY` (a random string)
    *   `INSTAGRAM_USERNAME`
    *   `INSTAGRAM_PASSWORD`
    *   `N8N_SMTP_HOST`
    *   `N8N_SMTP_PORT`
    *   `N8N_SMTP_USER`
    *   `N8N_SMTP_PASS` (use an App Password if 2FA is enabled)
    *   `N8N_SMTP_SENDER`
4.  **Trigger Workflow:** The workflow will run on its schedule, or you can manually trigger it from the GitHub Actions tab.

## 🚧 Future Considerations

*   **More Robust Health Check:** Implement a more sophisticated health check for the n8n service (e.g., checking a specific n8n API endpoint) instead of just `sleep`.
*   **Dynamic Hashtag Strategy:** Implement a system to dynamically select and combine hashtag groups for broader reach and less repetition.
*   **Automated Comment Replies:** (Highly complex) Integrate LLMs and Instagram API polling to understand and reply to comments, though this requires significant development and careful ethical consideration.

This project provides a solid foundation for automated Instagram content delivery, built with reliability and intelligence in mind.