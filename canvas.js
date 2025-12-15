// Dynamic multi-color background animation based on sentence content
const canvas = document.getElementById("background-canvas");
const ctx = canvas.getContext("2d");

let colorPalette = [
    [30, 30, 40],
    [20, 40, 60],
    [40, 20, 50],
    [10, 50, 80]
]; // Start with 4 colors

let targetPalette = [...colorPalette];
let animationSpeed = 0.015;
let movementPhase = 0;
let movementSpeed = 0.005;
let rotationPhase = 0;

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});

// Color keyword extraction and mapping (MORE VIBRANT)
const colorKeywords = {
    // Reds/Oranges (fire, heat, danger) - More vibrant
    'fire': [200, 80, 40],
    'flame': [220, 70, 30],
    'burn': [190, 70, 35],
    'heat': [200, 100, 50],
    'sun': [220, 130, 50],
    'lava': [210, 60, 30],
    'blood': [180, 30, 30],
    'red': [190, 50, 40],
    'orange': [220, 120, 40],
    
    // Blues (water, cold, sky) - More vibrant
    'ocean': [20, 90, 180],
    'water': [30, 110, 200],
    'sea': [25, 100, 190],
    'ice': [60, 120, 210],
    'glacier': [70, 130, 200],
    'blue': [30, 90, 200],
    'cold': [40, 100, 180],
    'sky': [50, 120, 210],
    'frozen': [65, 125, 205],
    
    // Greens (nature, forest, growth) - More vibrant
    'forest': [30, 120, 60],
    'tree': [40, 140, 70],
    'leaf': [50, 160, 65],
    'grass': [70, 160, 60],
    'green': [45, 140, 65],
    'moss': [50, 130, 70],
    'plant': [60, 150, 70],
    
    // Browns/Earth (soil, desert, decay) - More vibrant
    'desert': [180, 120, 60],
    'sand': [200, 150, 80],
    'soil': [150, 100, 60],
    'earth': [170, 120, 70],
    'mud': [130, 100, 70],
    'brown': [170, 110, 65],
    'dust': [190, 140, 80],
    'drought': [200, 130, 65],
    
    // Grays/Blacks (pollution, city, smoke) - Lighter for contrast
    'smoke': [90, 90, 110],
    'ash': [110, 110, 120],
    'pollution': [100, 90, 100],
    'city': [110, 110, 130],
    'concrete': [120, 120, 135],
    'gray': [110, 110, 120],
    'smog': [130, 120, 110],
    
    // Purples (twilight, toxicity) - More vibrant
    'purple': [140, 70, 180],
    'toxic': [120, 90, 160],
    'poison': [130, 80, 170],
    'dusk': [150, 90, 190],
    
    // Whites/Pale (bleached, death) - Keep darker for contrast
    'bleach': [140, 140, 160],
    'pale': [130, 130, 150],
    'ghost': [120, 120, 140],
    
    // Yellows (warning, decay) - More vibrant
    'yellow': [210, 200, 70],
    'decay': [180, 170, 80],
    'rot': [170, 160, 70]
};

function ensureDarkColor(rgb) {
    let [r, g, b] = rgb;
    // Remove the dark color restriction - allow vibrant colors
    // Just ensure they're not too bright (cap at 220 instead of 160)
    r = Math.min(220, r);
    g = Math.min(220, g);
    b = Math.min(220, b);
    return [r, g, b];
}

function extractColorsFromText(text, baseRgb) {
    const lowerText = text.toLowerCase();
    const foundColors = [];
    
    // Always include the base RGB from the line
    foundColors.push(ensureDarkColor(baseRgb));
    
    // Extract colors mentioned in text
    for (const [keyword, color] of Object.entries(colorKeywords)) {
        if (lowerText.includes(keyword)) {
            foundColors.push(ensureDarkColor(color));
        }
    }
    
    // If we found colors, use them; otherwise generate variations of base
    if (foundColors.length === 1) {
        // No keywords found, generate analogous colors from base
        const [r, g, b] = foundColors[0];
        foundColors.push(ensureDarkColor([
            Math.max(0, Math.min(220, r + 50)),
            Math.max(0, Math.min(220, g - 30)),
            Math.max(0, Math.min(220, b + 40))
        ]));
        foundColors.push(ensureDarkColor([
            Math.max(0, Math.min(220, r - 30)),
            Math.max(0, Math.min(220, g + 50)),
            Math.max(0, Math.min(220, b - 25))
        ]));
    }
    
    // Ensure we have at least 3-5 colors for richness
    while (foundColors.length < 4 && foundColors.length > 0) {
        const lastColor = foundColors[foundColors.length - 1];
        foundColors.push(ensureDarkColor([
            Math.max(0, Math.min(220, lastColor[0] + (Math.random() * 60 - 30))),
            Math.max(0, Math.min(220, lastColor[1] + (Math.random() * 60 - 30))),
            Math.max(0, Math.min(220, lastColor[2] + (Math.random() * 60 - 30)))
        ]));
    }
    
    return foundColors.slice(0, 5); // Max 5 colors
}

function analyzeSentiment(text) {
    const lowerText = text.toLowerCase();
    const urgentWords = ['fire', 'burn', 'rage', 'violent', 'crash', 'storm', 'explosion', 'shatter', 'collapse', 'dying', 'desperate', 'frantically', 'panic', 'destroy'];
    const calmWords = ['gentle', 'slow', 'peaceful', 'quiet', 'whisper', 'drift', 'lull', 'fade', 'soft', 'still', 'calm'];
    
    let urgency = 0;
    urgentWords.forEach(word => {
        if (lowerText.includes(word)) urgency += 1;
    });
    calmWords.forEach(word => {
        if (lowerText.includes(word)) urgency -= 0.5;
    });
    
    if (urgency > 2) return 0.025; // Very fast
    else if (urgency > 1) return 0.018; // Fast
    else if (urgency > 0) return 0.012; // Moderate
    else return 0.005; // Slow sway
}

function lerp(start, end, t) {
    return start + (end - start) * t;
}

function lerpColor(color1, color2, t) {
    return [
        lerp(color1[0], color2[0], t),
        lerp(color1[1], color2[1], t),
        lerp(color1[2], color2[2], t)
    ];
}

function drawMultiColorGradient() {
    // Smoothly transition colors
    for (let i = 0; i < colorPalette.length; i++) {
        colorPalette[i] = lerpColor(colorPalette[i], targetPalette[i] || targetPalette[0], animationSpeed);
    }
    
    movementPhase += movementSpeed;
    rotationPhase += movementSpeed * 0.3; // Slower rotation
    
    // Create multiple overlapping gradients for richness
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    
    // Draw multiple radial gradients from different positions
    for (let i = 0; i < colorPalette.length; i++) {
        const angle = (rotationPhase + (i * Math.PI * 2 / colorPalette.length));
        const radius = Math.min(canvas.width, canvas.height) * 0.3;
        
        const offsetX = Math.cos(angle) * radius + Math.sin(movementPhase + i) * 80;
        const offsetY = Math.sin(angle) * radius + Math.cos(movementPhase * 0.7 + i) * 80;
        
        const gradient = ctx.createRadialGradient(
            centerX + offsetX, centerY + offsetY, 0,
            centerX + offsetX, centerY + offsetY, canvas.width * 0.7
        );
        
        const [r, g, b] = colorPalette[i];
        const nextColor = colorPalette[(i + 1) % colorPalette.length];
        const [r2, g2, b2] = nextColor;
        
        gradient.addColorStop(0, `rgba(${r},${g},${b},0.7)`);
        gradient.addColorStop(0.5, `rgba(${(r+r2)/2},${(g+g2)/2},${(b+b2)/2},0.5)`);
        gradient.addColorStop(1, `rgba(${r2},${g2},${b2},0.3)`);
        
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
    
    requestAnimationFrame(drawMultiColorGradient);
}

function updateBackground(rgb, text) {
    // Extract multiple colors from the sentence
    const extractedColors = extractColorsFromText(text, rgb);
    targetPalette = extractedColors;
    
    // Update movement speed based on sentiment
    movementSpeed = analyzeSentiment(text);
    
    console.log(`Extracted ${extractedColors.length} colors from: "${text.substring(0, 50)}..."`);
}

drawMultiColorGradient();

// Export function for use in script.js
window.updateCanvasBackground = updateBackground;