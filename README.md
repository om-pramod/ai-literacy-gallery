# AI Literacy: Visual Storytelling & Technical Gallery

A premium, editorial-style web gallery that explains complex Artificial Intelligence concepts through the intersection of visual metaphors (memes) and rigorous technical deep dives. This project is a curated educational platform designed to make advanced AI concepts accessible, engaging, and high-performance.

🌐 **View the Web Gallery:** [https://om-pramod.github.io/ai-literacy-gallery/](https://om-pramod.github.io/ai-literacy-gallery/)

---

## 🚀 Project Overview

This repository hosts a high-performance educational engine that transforms technical concepts into a focused, digital magazine experience. It represents a journey from raw AI glossary mapping to a sophisticated, web-optimized portfolio.

### Key Features
*   **Focused Engagement:** The gallery uses a clean, vertical layout with generous whitespace to ensure the audience focuses on one lesson at a time, preventing information overload.
*   **Intelligent Alt-Text:** The build engine automatically extracts explanations for use as image alt-text, ensuring the platform is SEO-friendly and accessible by design.
*   **High-Performance Delivery:** Assets are processed through an automated **Sharp** pipeline, converting all technical memes into **WebP** format with lazy-loading for sub-second page speeds.
*   **AEO Optimized:** Integrated JSON-LD structured data and semantic HTML5 tags ensure the content is digestible by AI Answer Engines and search crawlers.

## 📂 Repository Structure

```
ai-literacy-gallery/
├── .github/
│   └── workflows/
│       └── deploy_gallery.yml  # Automates the Web Gallery deployment
├── captions/                   # Curated library of 60+ technical AI lessons
├── memes/                      # High-resolution visual metaphors
├── docs/                       # The optimized, production-ready static site
├── build.js                    # The Node.js-based static site generator
├── package.json                # Project dependencies and build scripts
└── README.md                   # Technical documentation
```

## 📖 The Development Journey: A Technical Narrative

This project evolved through several distinct phases of AI engineering and web optimization:

### Phase I: Visual Metaphor & Multimodal Mapping
The project began as a computer vision challenge: *How can we translate visual humor into technical literacy?* Leveraging **Azure Computer Vision**, I performed visual context analysis on meme templates to identify semantic anchors. By mapping these anchors to a custom-curated **AI Glossary**, the system could autonomously suggest technically relevant captions that matched the visual metaphor of the template.

### Phase II: Leveraging Cloud Infrastructure
Utilizing **Microsoft Azure** student credits, I accessed high-level Large Language Models (LLMs) to generate sophisticated, multi-tiered technical explanations. This phase focused on creating a "Human-in-the-loop" interface, allowing for the fine-tuning of AI-generated content to ensure technical accuracy and pedagogical value.

### Phase III: The Architecture of Performance
The final phase transformed the project into a public-facing educational platform. I engineered a custom static site generator in Node.js, implementing a **Sharp-powered image pipeline**. This ensured that the extensive collection of technical assets was delivered with modern performance standards, including WebP conversion, width-normalization, and native browser lazy-loading.

---

## 🛠️ Setup & Local Build

### 1. Requirements
*   Node.js (v18+)
*   npm

### 2. Build the Gallery
To generate the optimized static site locally:
```bash
npm install
npm run build
```
The output will be generated in the `/docs` directory.

### 3. Deployment
The project is configured for **GitHub Pages**. Every push to the `main` branch triggers an automated build and deployment to the `gh-pages` branch via GitHub Actions.

---

Built to prove that technical education doesn't have to be dry—it just needs a better delivery mechanism.
