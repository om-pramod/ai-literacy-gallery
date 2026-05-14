# AI Literacy: Meme Gallery & Automation Pipeline

An editorial-style web gallery and automated content pipeline that explains complex AI concepts through humor and technical deep dives. This project is a "multimodal content engine" designed to educate both tech-savvy professionals and curious beginners.

## 🚀 The Dual-Engine Project

This repository serves two primary purposes:

### 1. The Focused Web Gallery (Portfolio)
A beautifully designed, minimalist web gallery hosted on GitHub Pages. It features a "Focused Feed" with scroll-snapping and active focus logic to ensure deep engagement with every lesson.
*   **Aesthetic:** Clean, editorial, high-readability typography.
*   **Educational Depth:** Each entry includes a "Hook," a simple "Explainer," and a technical "Deep Dive."
*   **Automation:** Automatically rebuilds and deploys via GitHub Actions whenever new content is added.
*   **View it live:** `https://your-username.github.io/instagram-automation/`

### 2. The Instagram Content Pipeline
A robust, browser-based automation script that bypasses API restrictions by using **Playwright** to simulate human behavior.
*   **Mechanism:** Uses a headless Chrome browser to log in and post memes directly to Instagram.
*   **Resilience:** Replaces legacy API-based methods with modern browser automation.
*   **Scheduling:** Runs twice daily (9 AM and 5 PM UTC) via GitHub Actions.

## 📂 Repository Structure

```
instagram-automation/
├── .github/
│   └── workflows/
│       ├── deploy_gallery.yml      # Automates the Web Gallery deployment
│       └── publisher.yml           # Automates the Instagram posting
├── captions/
│   ├── posted/                     # History of published AI lessons
│   └── to_post/                    # Queue of upcoming AI literacy content
├── memes/                          # Image assets matched to captions
├── docs/                           # The generated static website
├── build.js                        # The Node.js gallery build engine
├── post_to_instagram.py            # The Playwright-based posting script
└── README.md                       # You are here
```

## ✨ Key Features

*   **Focused Engagement:** The web gallery uses `scroll-snap` to "lock" the audience onto one lesson at a time, preventing "doom-scrolling" past educational content.
*   **Intelligent Alt-Text:** The build engine automatically extracts explanations for use as image alt-text, improving SEO and accessibility.
*   **State Management:** Successfully posted memes are moved from `to_post/` to `posted/` and committed back to the repo automatically.
*   **Accessibility by Design:** Every post is designed to be readable for non-techies while providing "Deep Dive" value for engineers.

## 🛠️ Setup & Deployment

### 1. Web Gallery
1.  Go to **Settings > Pages** in this repository.
2.  Set the Source to **"Deploy from a branch"**.
3.  Set the Branch to `main` and the Folder to `/docs`.

### 2. Instagram Automation
Add the following to your **GitHub Actions Secrets**:
*   `INSTAGRAM_USERNAME`
*   `INSTAGRAM_PASSWORD`

## 🚧 Future Evolution
*   **Expanded Glossary:** Continuous updates to cover Agentic AI, LLM safety, and new hardware trends.
*   **Interactive Quizzes:** Future versions of the gallery may include simple "check your knowledge" interactions.

This project was built to prove that technical education doesn't have to be dry—it just needs a better delivery mechanism.
