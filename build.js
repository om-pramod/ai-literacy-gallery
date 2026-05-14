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

  // Remove leading/trailing dots and spaces
  Object.keys(sections).forEach(key => {
    sections[key] = sections[key].replace(/^(\s|\.|\n)+|(\s|\.|\n)+$/g, '');
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
      posts.push({
        title: baseName,
        memeUrl,
        ...parsed
      });
    }
  });
});

const htmlContent = `
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Literacy Gallery</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        body { 
            font-family: 'Inter', sans-serif; 
            background-color: #ffffff;
        }
        h1, h2, h3, .serif { 
            font-family: 'Playfair Display', serif; 
        }
        .snap-container {
            scroll-snap-type: y mandatory;
            height: 100vh;
            overflow-y: scroll;
        }
        .snap-section {
            scroll-snap-align: start;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 4rem 2rem;
            transition: opacity 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .snap-section:not(.active) {
            opacity: 0.1;
            filter: blur(2px);
        }
        /* Fix spacing in deep dive */
        .prose p {
            margin-bottom: 1.5rem;
            line-height: 1.75;
        }
        .prose li {
            margin-bottom: 0.75rem;
        }
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        ::-webkit-scrollbar-thumb {
            background: #e2e2e2;
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #cbd5e1;
        }
    </style>
</head>
<body class="text-slate-800">

    <div id="progress-bar" class="fixed top-0 left-0 h-1 bg-slate-900 z-50 transition-all duration-500" style="width: 0%"></div>

    <div class="snap-container">
        <!-- Introduction Card -->
        <section class="snap-section active">
            <div class="max-w-4xl text-center">
                <span class="text-xs uppercase tracking-[0.3em] text-slate-400 font-semibold mb-4 block">Curated Collection</span>
                <h1 class="text-7xl font-bold mb-8 text-slate-900">AI Literacy</h1>
                <p class="text-2xl text-slate-500 italic max-w-2xl mx-auto leading-relaxed">A visual journey through complex intelligence, explained simply.</p>
                <div class="mt-20 animate-pulse text-slate-300">
                    <svg class="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path></svg>
                </div>
            </div>
        </section>

        ${posts.map((post, index) => `
        <section class="snap-section" id="post-${index}">
            <div class="max-w-6xl w-full grid grid-cols-1 lg:grid-cols-12 gap-16 items-start">
                
                <!-- Meme Column -->
                <div class="lg:col-span-6 sticky top-20">
                    <div class="bg-slate-50 p-4 rounded-2xl">
                        <img src="${post.memeUrl}" alt="${post.title}" class="w-full h-auto rounded-lg shadow-2xl transition-transform duration-700 hover:scale-[1.02]">
                    </div>
                </div>
                
                <!-- Content Column -->
                <div class="lg:col-span-6 pt-4">
                    <header class="mb-12">
                        <h2 class="text-4xl font-bold mb-6 text-slate-900 leading-tight">${post.title}</h2>
                        <div class="h-px w-20 bg-slate-200 mb-8"></div>
                        <p class="text-xl leading-relaxed text-slate-600 italic">
                            ${post.hook.replace(/\\n/g, '<br>')}
                        </p>
                    </header>

                    <div class="space-y-12">
                        <section>
                            <h3 class="text-xs uppercase tracking-[0.2em] text-slate-400 font-bold mb-4">Context</h3>
                            <p class="text-lg text-slate-700 leading-relaxed font-medium">
                                ${post.explainer}
                            </p>
                        </section>

                        <section class="prose prose-slate max-w-none border-t border-slate-100 pt-8">
                            <h3 class="text-xs uppercase tracking-[0.2em] text-slate-400 font-bold mb-6">Technical Insight</h3>
                            <div class="text-slate-600 text-[1.05rem]">
                                ${marked(post.deepDive)}
                            </div>
                        </section>
                    </div>
                </div>
            </div>
        </section>
        `).join('')}

        <!-- End Card -->
        <section class="snap-section">
            <div class="max-w-2xl text-center">
                <h2 class="text-4xl font-bold mb-6 text-slate-900">Knowledge is Continuous.</h2>
                <p class="text-slate-500 mb-12 text-lg">You've reached the end of the current collection. New concepts are added as the field evolves.</p>
                <button onclick="document.querySelector('.snap-container').scrollTo({top: 0, behavior: 'smooth'})" class="border-2 border-slate-900 text-slate-900 px-10 py-4 rounded-full font-bold hover:bg-slate-900 hover:text-white transition-all duration-300">
                    Return to Top
                </button>
            </div>
        </section>
    </div>

    <script>
        const sections = document.querySelectorAll('.snap-section');
        const progressBar = document.getElementById('progress-bar');
        const container = document.querySelector('.snap-container');

        const observerOptions = {
            root: container,
            threshold: 0.5
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    sections.forEach(s => s.classList.remove('active'));
                    entry.target.classList.add('active');
                    
                    const index = Array.from(sections).indexOf(entry.target);
                    const progress = (index / (sections.length - 1)) * 100;
                    progressBar.style.width = \`\${progress}%\`;
                }
            });
        }, observerOptions);

        sections.forEach(section => observer.observe(section));
    </script>
</body>
</html>
`;

fs.writeFileSync(path.join(OUTPUT_DIR, 'index.html'), htmlContent);
console.log('Gallery built successfully in /docs');
