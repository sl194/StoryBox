const lands = document.querySelectorAll(".land");
const storyLinesContainer = document.getElementById("story-lines");
const landscapePanel = document.getElementById("landscape-panel");
const storyContainer = document.getElementById("story-container");

let allLines = [];
let currentIndex = -1;

function clearActive() {
    lands.forEach(l => l.classList.remove("active"));
}

function highlightLandscape(name) {
    clearActive();
    const el = document.querySelector(`.land[data-name="${name}"]`);
    if (el) {
        el.classList.add("active");
        scrollToActiveChip();
    }
}

function scrollToActiveChip() {
    const activeChip = document.querySelector('.land.active');
    if (activeChip && landscapePanel) {
        const containerWidth = landscapePanel.offsetWidth;
        const chipOffsetLeft = activeChip.offsetLeft;
        const chipWidth = activeChip.offsetWidth;
        
        const scrollPosition = chipOffsetLeft - (containerWidth / 2) + (chipWidth / 2);
        
        landscapePanel.scrollTo({
            left: scrollPosition,
            behavior: 'smooth'
        });
    }
}

function scrollToActiveLine() {
    const activeLine = document.querySelector('.story-line.active');
    if (!activeLine || !storyContainer) {
        console.log("No active line or container found");
        return;
    }
    
    console.log("Scrolling to active line");
    
    // Scroll so active line has 10vh gap from bottom
    const containerHeight = storyContainer.clientHeight;
    const lineOffsetTop = activeLine.offsetTop;
    const tenVh = window.innerHeight * 0.1; // 10% of viewport height
    
    // Position active line 10vh from bottom
    const targetScroll = lineOffsetTop - containerHeight + tenVh + activeLine.offsetHeight;
    
    console.log(`Container height: ${containerHeight}, Line offset: ${lineOffsetTop}, Target scroll: ${targetScroll}`);
    
    storyContainer.scrollTo({
        top: Math.max(0, targetScroll),
        behavior: 'smooth'
    });
}

// Poll JSON every 500ms
async function pollJSON() {
    try {
        const res = await fetch(`story.json?cache=${Date.now()}`);
        if (!res.ok) return;

        const data = await res.json();
        
        // Update background animation
        if (data.rgb && data.rgb.length === 3 && window.updateCanvasBackground) {
            window.updateCanvasBackground(data.rgb, data.text);
        }

        // Highlight the active landscape
        highlightLandscape(data.landscape);

        // Check if we have a new line
        if (data.index !== currentIndex) {
            currentIndex = data.index;
            
            // Add new line if it doesn't exist
            if (!allLines[currentIndex]) {
                allLines[currentIndex] = {
                    text: data.text,
                    landscape: data.landscape,
                    rgb: data.rgb
                };
                renderLines();
            }
        }

    } catch (err) {
        console.error("JSON load error:", err);
    }
}

function renderLines() {
    // Keep all lines visible, just update their states
    if (allLines.length === 1 && storyLinesContainer.children.length === 1) {
        storyLinesContainer.innerHTML = '';
    }
    
    // Add any new lines that don't exist yet
    while (storyLinesContainer.children.length < allLines.length) {
        const lineEl = document.createElement('div');
        lineEl.className = 'story-line future';
        storyLinesContainer.appendChild(lineEl);
    }
    
    // Update all line states and content
    allLines.forEach((line, idx) => {
        const lineEl = storyLinesContainer.children[idx];
        lineEl.textContent = line.text;
        
        lineEl.className = 'story-line';
        
        if (idx < currentIndex) {
            lineEl.classList.add('past');
        } else if (idx === currentIndex) {
            lineEl.classList.add('active');
            
            // Multiple attempts to ensure scroll happens
            setTimeout(() => scrollToActiveLine(), 50);
            setTimeout(() => scrollToActiveLine(), 200);
            setTimeout(() => scrollToActiveLine(), 500);
        } else {
            lineEl.classList.add('future');
        }
    });
}

// Auto-scroll on window resize
window.addEventListener('resize', scrollToActiveChip);

// Initialize scroll on page load
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(scrollToActiveChip, 100);
});

// Poll every 500ms
setInterval(pollJSON, 500);

document.addEventListener('DOMContentLoaded', function() {
    const storyLinesDiv = document.getElementById('story-lines');
    const storyLinePlaceholder = storyLinesDiv.querySelector('.story-line');
    
    const loadingText = "Waiting for story..."; 
    const textLength = loadingText.length;
    // Set speed: 0.1s per character is a good rate (3 seconds for 30 characters)
    const typingDuration = textLength * 0.1; 
    
    // 1. Wrap the text in an inner span for animation control
    storyLinePlaceholder.innerHTML = `<span class="typing-text">${loadingText}</span>`;
    const typingSpan = storyLinePlaceholder.querySelector('.typing-text');
    
    // 2. Apply the animations
    typingSpan.style.animation = 
        `typing ${typingDuration}s steps(${textLength}, end) forwards, 
         blink-caret 0.75s step-end infinite`; 
         
    // 'forwards' ensures the text stays visible after typing finishes.

    // 3. Define a function to remove the effect when the real story arrives
    window.injectRealStory = function(realStoryContent) {
        // Stop the animation and remove the cursor border
        typingSpan.style.animation = 'none'; 
        typingSpan.style.borderRight = 'none';
        
        // Remove the placeholder content and replace with the story
        storyLinePlaceholder.innerHTML = realStoryContent;
        storyLinePlaceholder.classList.remove('typing-effect');
        
        // You'll likely need to add the necessary active/opacity classes here
        // once the story lines are dynamically created.
    };
});