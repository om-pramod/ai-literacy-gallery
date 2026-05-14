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
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Lora:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .serif { font-family: 'Lora', serif; }
        .snap-container {
            scroll-snap-type: y mandatory;
            height: 100vh;
            overflow-y: scroll;
        }
        .snap-section {
            scroll-snap-align: start;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            transition: opacity 0.5s ease;
        }
        .snap-section:not(.active) {
            opacity: 0.3;
            filter: grayscale(0.5);
        }
    </style>
</head>
<body class="bg-gray-50 text-gray-900">

    <div id="progress-bar" class="fixed top-0 left-0 h-1 bg-blue-600 z-50 transition-all duration-300" style="width: 0%"></div>

    <div class="snap-container">
        <!-- Introduction Card -->
        <section class="snap-section active">
            <div class="max-w-3xl text-center">
                <h1 class="text-5xl font-bold mb-6">AI Literacy Gallery</h1>
                <p class="text-xl text-gray-600 serif italic">A collection of AI concepts explained through memes and technical deep dives.</p>
                <div class="mt-12 animate-bounce text-gray-400">
                    <p>Scroll down to begin</p>
                    <svg class="w-6 h-6 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path></svg>
                </div>
            </div>
        </section>

        ${posts.map((post, index) => `
        <section class="snap-section" id="post-${index}">
            <div class="bg-white rounded-xl shadow-lg overflow-hidden max-w-5xl w-full flex flex-col md:flex-row h-full max-h-[90vh]">
                <!-- Meme Column -->
                <div class="md:w-1/2 bg-gray-100 flex items-center justify-center p-4 border-r border-gray-100">
                    <img src="${post.memeUrl}" alt="${post.title}" class="max-h-full max-w-full object-contain shadow-sm">
                </div>
                
                <!-- Content Column -->
                <div class="md:w-1/2 p-8 overflow-y-auto flex flex-col bg-white">
                    <div class="mb-6">
                        <h2 class="text-2xl font-bold mb-4 text-gray-800">${post.title}</h2>
                        <p class="text-lg leading-relaxed text-gray-700 serif italic">"${post.hook}"</p>
                    </div>

                    <div class="mb-8 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
                        <h3 class="text-sm font-bold uppercase tracking-wider text-blue-600 mb-2">🧐 For those who don't get it</h3>
                        <p class="text-gray-700 leading-snug">${post.explainer}</p>
                    </div>

                    <div class="prose prose-blue flex-grow">
                        <h3 class="text-sm font-bold uppercase tracking-wider text-gray-500 mb-4">🧠 Techie Deep Dive</h3>
                        <div class="text-gray-600 leading-relaxed serif">
                            ${marked(post.deepDive)}
                        </div>
                    </div>
                </div>
            </div>
        </section>
        `).join('')}

        <!-- End Card -->
        <section class="snap-section">
            <div class="max-w-2xl text-center">
                <h2 class="text-3xl font-bold mb-4">You've reached the end!</h2>
                <p class="text-gray-600 mb-8">Hope these memes helped shed some light on the world of AI.</p>
                <button onclick="window.scrollTo({top: 0, behavior: 'smooth'})" class="bg-blue-600 text-white px-6 py-3 rounded-full font-bold hover:bg-blue-700 transition">Back to Start</button>
            </div>
        </section>
    </div>

    <script>
        const sections = document.querySelectorAll('.snap-section');
        const progressBar = document.getElementById('progress-bar');
        const container = document.querySelector('.snap-container');

        const observerOptions = {
            root: container,
            threshold: 0.6
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    sections.forEach(s => s.classList.remove('active'));
                    entry.target.classList.add('active');
                    
                    // Update Progress
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
