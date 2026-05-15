const fs = require('fs');
const path = require('path');
const { marked } = require('marked');

const CAPTIONS_DIRS = ['captions/to_post', 'captions/posted'];
const MEMES_DIR = 'memes';
const OUTPUT_DIR = 'docs';

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR);
}

// Copy memes to docs/memes for web access
const webMemesDir = path.join(OUTPUT_DIR, 'memes');
if (!fs.existsSync(webMemesDir)) {
  fs.mkdirSync(webMemesDir);
}

function getMemePath(baseName) {
  const extensions = ['.png', '.jpg', '.jpeg'];
  for (const ext of extensions) {
    const fullPath = path.join(MEMES_DIR, baseName + ext);
    if (fs.existsSync(fullPath)) {
      // Copy to docs/memes
      const destPath = path.join(webMemesDir, baseName + ext);
      fs.copyFileSync(fullPath, destPath);
      return `memes/${baseName}${ext}`;
    }
  }
  return null;
}

function parseCaption(content) {
  const sections = {
    hook: '',
    explainer: '',
    deepDive: ''
  };

  const explainerMarker = "🧐 For those who don't get it:";
  const deepDiveMarker = "🧠 Techie Deep Dive:";
  const hashtagMarker = "\n#";

  let workingContent = content;

  // Extract Hook
  const explainerIndex = workingContent.indexOf(explainerMarker);
  if (explainerIndex !== -1) {
    sections.hook = workingContent.substring(0, explainerIndex).trim();
    workingContent = workingContent.substring(explainerIndex);
  } else {
    sections.hook = workingContent.trim();
    return sections;
  }

  // Extract Explainer
  const deepDiveIndex = workingContent.indexOf(deepDiveMarker);
  if (deepDiveIndex !== -1) {
    sections.explainer = workingContent.substring(explainerMarker.length, deepDiveIndex).trim();
    workingContent = workingContent.substring(deepDiveIndex);
  } else {
    sections.explainer = workingContent.substring(explainerMarker.length).trim();
    return sections;
  }

  // Extract Deep Dive
  const hashIndex = workingContent.indexOf(hashtagMarker);
  if (hashIndex !== -1) {
    sections.deepDive = workingContent.substring(deepDiveMarker.length, hashIndex).trim();
  } else {
    sections.deepDive = workingContent.substring(deepDiveMarker.length).trim();
  }

  // CLEANUP AND FORMATTING
  Object.keys(sections).forEach(key => {
    // Remove leading/trailing dots and spaces
    sections[key] = sections[key].replace(/^(\s|\.|\n)+|(\s|\.|\n)+$/g, '');
    
    // Normalize bullets for Markdown (convert • to -)
    if (key === 'deepDive') {
      sections[key] = sections[key].replace(/•\s*/g, '\n- ');
    }
  });

  return sections;
}

const posts = [];

CAPTIONS_DIRS.forEach(dir => {
  if (!fs.existsSync(dir)) return;
  
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.md'));
  files.forEach(file => {
    const content = fs.readFileSync(path.join(dir, file), 'utf-8');
    const baseName = path.basename(file, '.md');
    const memeUrl = getMemePath(baseName);
    
    if (memeUrl) {
      const parsed = parseCaption(content);
      // CLEAN TITLE: Remove trailing numbers like (1)
      const cleanTitle = baseName.replace(/\s\(\d+\)$/, '');
      posts.push({
        title: cleanTitle,
        memeUrl,
        ...parsed
      });
    }
  });
});

const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Literacy Gallery | Explaining AI through Memes</title>
    <meta name="description" content="A curated collection of AI concepts explained through memes and technical deep dives. Learn about Reinforcement Learning, Differential Privacy, and more.">
    <meta name="keywords" content="AI Literacy, Machine Learning, AI Memes, Data Science Education, Technical Explainer">
    <meta property="og:title" content="AI Literacy Gallery">
    <meta property="og:description" content="Complex AI concepts, explained simply through memes.">
    <meta name="robots" content="index, follow">
    
    <!-- AEO / Structured Data -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "EducationalOccupationalCredential",
      "name": "AI Literacy Meme Gallery",
      "description": "Educational resource for learning AI fundamentals through visual metaphors and technical deep dives.",
      "educationalLevel": "Beginner to Intermediate"
    }
    </script>

    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #ffffff;
            --text-main: #1e293b;
        }
        html, body {
            margin: 0;
            padding: 0;
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
        }
        h1, h2, h3, .serif { 
            font-family: 'Playfair Display', serif; 
        }
        .section-container {
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 8rem 5vw;
            box-sizing: border-box;
            border-bottom: 1px solid #f1f5f9;
        }
        .prose p {
            margin-bottom: 1.5rem;
            line-height: 1.8;
        }
        .prose ul {
            list-style-type: disc;
            margin-left: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .prose ol {
            list-style-type: decimal;
            margin-left: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .prose li {
            margin-bottom: 0.75rem;
            line-height: 1.6;
        }
    </style>
</head>
<body>

    <div id="progress-bar" class="fixed top-0 left-0 h-1 bg-slate-900 z-50 transition-all duration-300" style="width: 0%"></div>

    <!-- Introduction Card -->
    <header class="section-container text-center">
        <div class="max-w-4xl">
            <span class="text-xs uppercase tracking-[0.3em] text-slate-400 font-semibold mb-4 block">Curated Collection</span>
            <h1 class="text-7xl font-bold mb-8">AI Literacy</h1>
            <p class="text-2xl text-slate-500 italic max-w-2xl mx-auto leading-relaxed">A visual journey through complex intelligence, explained simply.</p>
        </div>
    </header>

    <main>
    ${posts.map((post, index) => `
    <article class="section-container" id="post-${index}">
        <div class="max-w-6xl w-full grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-20 items-start relative">
            
            <!-- Topic Counter -->
            <div class="absolute -top-12 left-0 w-full flex items-center gap-4">
                <span class="text-[10px] uppercase tracking-[0.4em] text-slate-300 font-bold whitespace-nowrap">Topic ${String(index + 1).padStart(2, '0')} of ${String(posts.length).padStart(2, '0')}</span>
                <div class="h-[0.5px] w-full bg-slate-100"></div>
            </div>

            <!-- Meme Column -->
            <div class="lg:col-span-6 flex justify-center lg:sticky lg:top-12">
                <div class="bg-slate-50 p-2 lg:p-4 rounded-2xl shadow-sm border border-slate-100">
                    <img src="${post.memeUrl}" alt="${post.title}" class="w-full h-auto rounded-lg shadow-xl">
                </div>
            </div>
            
            <!-- Content Column -->
            <div class="lg:col-span-6 py-4">
                <header class="mb-10">
                    <p class="text-xl leading-relaxed text-slate-700 font-medium">
                        ${post.hook.replace(/\\n/g, '<br>')}
                    </p>
                    <div class="h-px w-16 bg-slate-200 mt-8"></div>
                </header>

                <div class="space-y-10">
                    <section>
                        <h3 class="text-xs uppercase tracking-[0.2em] text-slate-400 font-bold mb-4">The Context</h3>
                        <p class="text-lg text-slate-700 leading-relaxed">
                            ${post.explainer}
                        </p>
                    </section>

                    <section class="prose prose-slate max-w-none border-t border-slate-100 pt-8">
                        <h3 class="text-xs uppercase tracking-[0.2em] text-slate-400 font-bold mb-6">Technical Insight</h3>
                        <div class="text-slate-600 text-[1.1rem]">
                            ${marked(post.deepDive)}
                        </div>
                    </section>
                </div>
            </div>
        </div>
    </article>
    `).join('')}
    </main>

    <!-- End Card -->
    <footer class="section-container text-center">
        <div class="max-w-2xl">
            <h2 class="text-4xl font-bold mb-6">Knowledge is Continuous.</h2>
            <p class="text-slate-500 mb-12 text-lg">You've reached the end of the current collection. New concepts are added as the field evolves.</p>
            <button onclick="window.scrollTo({top: 0, behavior: 'smooth'})" class="border-2 border-slate-900 text-slate-900 px-10 py-4 rounded-full font-bold hover:bg-slate-900 hover:text-white transition-all duration-300">
                Return to Top
            </button>
        </div>
    </footer>

    <script>
        const progressBar = document.getElementById('progress-bar');
        window.addEventListener('scroll', () => {
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (winScroll / height) * 100;
            progressBar.style.width = scrolled + "%";
        });
    </script>
</body>
</html>
`;

fs.writeFileSync(path.join(OUTPUT_DIR, 'index.html'), htmlContent);
console.log('Gallery built successfully in /docs');
