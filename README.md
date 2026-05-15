# AI Literacy: Meme Gallery & Automation Pipeline

An editorial-style web gallery and automated content pipeline that explains complex AI concepts through humor and technical deep dives. This project is a "multimodal content engine" designed to educate both tech-savvy professionals and curious beginners.

## 🚀 The Dual-Engine Project

This repository serves two primary purposes:

### 1. The Focused Web Gallery (Portfolio)
A beautifully designed, minimalist web gallery hosted on GitHub Pages. It features a "Focused Feed" with scroll-snapping and active focus logic to ensure deep engagement with every lesson.
*   **Aesthetic:** Clean, editorial, high-readability typography.
*   **Educational Depth:** Each entry includes a "Hook," a simple "Explainer," and a technical "Deep Dive."
*   **Automation:** Automatically rebuilds and deploys via GitHub Actions whenever new content is added.
*   **View it live:** `https://om-pramod.github.io/ai-literacy-gallery/`

### 2. The Instagram Content Pipeline
A robust, browser-based automation script that bypasses API restrictions by using **Playwright** to simulate human behavior.
*   **Mechanism:** Uses a headless Chrome browser to log in and post memes directly to Instagram.
*   **Resilience:** Replaces legacy API-based methods with modern browser automation.
*   **Scheduling:** Runs twice daily (9 AM and 5 PM UTC) via GitHub Actions.

## 📂 Repository Structure

```
ai-literacy-gallery/
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

*   **Focused Engagement:** The web gallery uses `scroll-snap` logic to ensure deep engagement with one lesson at a time.
*   **Intelligent Alt-Text:** The build engine automatically extracts explanations for use as image alt-text, improving SEO and accessibility.
*   **High-Performance Delivery:** Automated **Sharp** pipeline converts all assets to WebP with lazy-loading for sub-second page speeds.
*   **AEO Optimized:** Integrated JSON-LD structured data for discovery by AI Answer Engines.

## 📖 The Development Journey: A Technical Narrative

This project evolved through several distinct phases of AI engineering and automation strategy:

### Phase I: The Vision & Multimodal Mapping
The project began as a challenge: *How can we translate visual humor into technical literacy?* Leveraging **Azure Computer Vision**, I scrapped blank meme templates and performed visual context analysis to identify text placement coordinates. By mapping these visual "anchors" to a custom-curated **AI Glossary**, the system could autonomously suggest technically relevant captions that matched the visual metaphor of the meme.

### Phase II: Leveraging Student Cloud Infrastructure
As a student explorer of the **Microsoft Azure** ecosystem, I utilized student credits to access high-level LLMs for sophisticated caption generation. This phase focused on creating a "Human-in-the-loop" interface, allowing for the fine-tuning of AI-generated content before it entered the automation pipeline.

### Phase III: The Pivot to Browser-Level Resilience
When standard API-based automation (instagrapi) met the resistance of evolving platform restrictions, the engine was refactored for **Resilience Engineering**. I pivoted the delivery mechanism to **Playwright**, an industrial-grade browser automation framework. By simulating authentic human interaction within a headless Chrome environment, the bot bypassed API limitations while maintaining strict security protocols.

### Phase IV: The Portfolio Pivot & Performance Optimization
The final phase transformed the project from a background bot into a public-facing educational platform. I engineered a custom static site generator in Node.js, implementing a **Sharp-powered image pipeline** to ensure the 60+ technical lessons were delivered with modern performance standards (WebP compression and lazy-loading).

---

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
