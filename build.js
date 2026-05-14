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
    <title>AI Literacy Gallery</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
        }
        body { 
            margin: 0;
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            scroll-snap-type: y mandatory;
        }
        h1, h2, h3, .serif { 
            font-family: 'Playfair Display', serif; 
        }
        .snap-section {
            scroll-snap-align: start;
            min-height: 100vh;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 5vh 5vw;
            box-sizing: border-box;
            border-bottom: 1px solid #f1f5f9;
        }
        .prose p {
            margin-bottom: 1.5rem;
            line-height: 1.8;
        }
        /* Custom Scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #f8fafc; }
        ::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
    </style>
</head>
<body>

    <div id="progress-bar" class="fixed top-0 left-0 h-1 bg-slate-900 z-50" style="width: 0%"></div>

    <!-- Introduction Card -->
    <section class="snap-section">
        <div class="max-w-4xl text-center">
            <span class="text-xs uppercase tracking-[0.3em] text-slate-400 font-semibold mb-4 block">Curated Collection</span>
            <h1 class="text-7xl font-bold mb-8">AI Literacy</h1>
            <p class="text-2xl text-slate-500 italic max-w-2xl mx-auto leading-relaxed">A visual journey through complex intelligence, explained simply.</p>
            <div class="mt-20 text-slate-300">
                <svg class="w-8 h-8 mx-auto animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path></svg>
            </div>
        </div>
    </section>

    ${posts.map((post, index) => `
    <article class="snap-section" id="post-${index}">
        <div class="max-w-6xl w-full grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-20 items-start">
            
            <!-- Meme Column -->
            <div class="lg:col-span-6 flex justify-center lg:sticky lg:top-12">
                <div class="bg-slate-50 p-2 lg:p-4 rounded-2xl shadow-sm border border-slate-100">
                    <img src="${post.memeUrl}" alt="${post.title}" class="w-full h-auto rounded-lg shadow-xl">
                </div>
            </div>
            
            <!-- Content Column -->
            <div class="lg:col-span-6 py-4">
                <header class="mb-10">
                    <h2 class="text-4xl font-bold mb-6 leading-tight">${post.title}</h2>
                    <div class="h-px w-16 bg-slate-200 mb-8"></div>
                    <p class="text-xl leading-relaxed text-slate-600 italic">
                        ${post.hook.replace(/\\n/g, '<br>')}
                    </p>
                </header>

                <div class="space-y-10">
                    <section>
                        <h3 class="text-xs uppercase tracking-[0.2em] text-slate-400 font-bold mb-4">The Context</h3>
                        <p class="text-lg text-slate-700 leading-relaxed font-medium">
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

    <!-- End Card -->
    <section class="snap-section">
        <div class="max-w-2xl text-center">
            <h2 class="text-4xl font-bold mb-6">Knowledge is Continuous.</h2>
            <p class="text-slate-500 mb-12 text-lg">You've reached the end of the current collection. New concepts are added as the field evolves.</p>
            <button onclick="window.scrollTo({top: 0, behavior: 'smooth'})" class="border-2 border-slate-900 text-slate-900 px-10 py-4 rounded-full font-bold hover:bg-slate-900 hover:text-white transition-all duration-300">
                Return to Top
            </button>
        </div>
    </section>

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
