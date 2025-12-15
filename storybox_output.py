#!/usr/bin/env python3
import sys, time, random, json, subprocess
import serial, serial.tools.list_ports
from pathlib import Path
import requests


# USER CONFIGURATION

USE_MOCK_DATA = False #True
BAUD = 115200
STORY_TYPE_MODE = "RANDOM" #RANDOM, #EMOTIONAL, #DATA
OUTPUT_MODE = "COMBINED" #DISPLAY, #SPOKEN, #COMBINED
TTS_MODE = "openai" #openai, #macsay 

OPENAI_API_KEY  = "" #add your own api key
OPENAI_TTS_MODEL = "gpt-4o-audio-preview"

EMOTION_VOICES = ["fable", "nova", "ballad", "meadow", "clover"]
DATA_VOICES = ["alloy", "echo", "coral", "verse", "onyx"]

STORY_LANGUAGE = "English"  #change language (doesn't work for now, not supported)

PORT_HINTS = ["usbmodem", "usbserial", "COM", "ttyACM", "ttyUSB"]
ACK_AFTER_SPEAK = True


def get_mock_environment():
    return {
        "T": random.uniform(15.0, 35.0),
        "H": random.uniform(30.0, 80.0),
        "WIND": random.uniform(0.0, 15.0),
        "DEPTH": random.uniform(5.0, 25.0)
    }


WEB_JSON_PATH = "story.json" 

def write_web_json(line_index, text, landscape, rgb):
    payload = {
        "index": line_index,
        "text": text,
        "landscape": landscape,
        "rgb": rgb
    }
    with open(WEB_JSON_PATH, "w") as f:
        json.dump(payload, f)


def pick_port():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("❌ No serial ports found.")
        sys.exit(1)

    for p in ports:
        name = (p.device or "").lower()
        desc = (p.description or "").lower()
        if any(h in name for h in PORT_HINTS) or any(h in desc for h in PORT_HINTS):
            return p.device

    return ports[0].device


def choose_story_type():
    if STORY_TYPE_MODE == "EMOTIONAL": return "emotional"
    if STORY_TYPE_MODE == "DATA": return "data"
    return random.choice(["emotional", "data"])

def choose_voice(story_type):
    if story_type == "emotional":
        return random.choice(EMOTION_VOICES)
    return random.choice(DATA_VOICES)


def build_prompt(env, story_type):
    water_level = max(0, 4 - env["DEPTH"])

    surprising_causes = [
        "algae blooms in distant seas creating new atmospheric aerosols",
        "the deep-ocean currents slowing down, altering global heat distribution",
        "permafrost thaw releasing long-dormant methane that accelerates heating",
        "fruit now growing thousands of kilometers outside its native climate",
        "turtles changing migration routes due to altered ocean salinity",
        "polar bears abandoning hunting grounds as the ice collapses",
        "desert dust shifting rainfall patterns on distant continents",
        "ocean heatwaves changing the jet stream",
        "glacial melt disrupting the lifecycles of mountain insects",
        "urban pollution altering cloud formation in rural regions",
        "ocean temperature shifts changing the speed of sound underwater, disrupting whale communication",
        "tropical insects and diseases surviving milder winters, fundamentally altering temperate forests",
        "thawing permafrost releasing ancient, long-dormant viruses and bacteria",
        "global warming altering the density of the upper atmosphere, increasing drag on low-orbit satellites",
        "rising water temperatures forcing major power plants to reduce output during peak heat demand",
        "the specific terroir for high-quality wine production relocating to unexpected regions like England",
        "cleaner shipping fuel reducing the reflective aerosol mask, inadvertently accelerating warming",
        "warmer oceans causing many fish species to shrink over generations due to lack of oxygen",
        "permafrost thaw causing critical infrastructure like airport runways to subside and crack"
    ]

    cause = random.choice(surprising_causes)

    if story_type == "emotional":
        prompt = f"""
You are writing ONE connected climate story that visits SEVEN landscapes in sequence:
ocean → countryside → city → glacier → mountain → forest → desert

Current environmental signals:
- Temperature: {env['T']}°C
- Humidity: {env['H']}%
- Wind: {env['WIND']} mph

Create a deeply emotional, poetic narrative showing how climate change ripples through these connected ecosystems.

CRITICAL STRUCTURE RULES:
1. Visit EACH landscape EXACTLY ONCE in the order above
2. Write 3-5 sentences per landscape (total: 21-35 sentences)  
3. Each sentence gets its own line with format: [SENTENCE][LANDSCAPE=name][R=xxx,G=xxx,B=xxx]
4. Connect landscapes through this surprising link: "{cause}"
5. Show how changes cascade from one place to another
6. DO NOT use headers or titles like "###Ocean" - just write the sentences

WRITING STYLE:
- Create atmospheric, sensory-rich descriptions like "the rain started just before the sun rose, and didn't stop for 24 hours"
- Focus on events that become permanent markers in collective memory, dividing "before" from "after"
- Show how communities are fundamentally changed long after the immediate crisis passes
- Build lingering anxiety and visceral dread that persists even when conditions appear normal
- Include specific, haunting details like contaminated floodwaters, displaced residents, and the psychological toll
- Make the reader feel the weight of what's been lost and the fear of what might come next

RGB COLOR RULES (DARK RANGES ONLY):
Match each sentence's imagery:
- Fire/heat/danger: R=120-160, G=40-80, B=20-50
- Water/cold/sadness: R=10-50, G=50-90, B=100-140  
- Nature/growth/decay: R=20-60, G=70-110, B=30-70
- Earth/drought/desert: R=90-130, G=60-100, B=30-60
- Pollution/city/loss: R=50-80, G=50-80, B=50-90
- Toxicity/dusk: R=70-110, G=40-80, B=90-130

EXAMPLE:
The ocean swells with fever, its waters growing too warm for the coral below.[LANDSCAPE=ocean][R=30,G=70,B=120]
Reefs that once bloomed with color now stand as white graveyards.[LANDSCAPE=ocean][R=80,G=80,B=100]
The salt-heavy air drifts inland, poisoning the countryside's once-fertile soil.[LANDSCAPE=countryside][R=100,G=80,B=50]

Write ONE continuous story visiting all 7 landscapes in order, 3-5 sentences each.
"""
    else:  # data-driven
        prompt = f"""
You are writing ONE connected environmental analysis that examines SEVEN landscapes:
ocean → countryside → city → glacier → mountain → forest → desert

Environmental indicators:
- Temperature anomaly: {env['T']}°C above historical average
- Humidity index: {env['H']}% relative humidity
- Wind disturbance: {env['WIND']} mph sustained winds

Create a data-driven narrative with concrete numbers and accessible explanations.

CRITICAL OUTPUT FORMAT RULES (MUST FOLLOW EXACTLY):
1. You MUST write 3–5 sentences per landscape.
2. Each sentence MUST end with a period **and then immediately break to a new line**.
3. **NEVER** place more than one sentence on the same line.
4. **NEVER** produce paragraphs. No grouping. No continuous blocks.
5. Each line must follow this exact format:
   [FULL SENTENCE][LANDSCAPE=name][R=xxx,G=xxx,B=xxx]
6. Lines must appear **one after another**, each ending with a newline.
7. Do NOT skip any of the seven landscapes.
8. Visit them in EXACT sequence: ocean → countryside → city → glacier → mountain → forest → desert
9. Connect them using this surprising causal chain: "{cause}"

WRITING REQUIREMENTS:
- Use ONLY meaningful, real-world measurements that people understand:
  * Temperature changes in °C or °F
  * Rainfall in inches, centimeters, or months-worth
  * Sea level rise in centimeters or feet
  * Ice loss in square kilometers or percentage
  * Time periods in days, months, years
  * Economic costs in dollars with context
  * Population impacts in actual numbers of people
- NEVER use vague terms like "units," "levels," "index" without clear meaning
- NEVER specify particular years - use "this year," "in recent years," "over the past decade," "historically" instead
- Include specific data points like "three months of rain fell in 24 hours" and "1,200 homes damaged"
- Track economic impacts with concrete figures for insurance payouts and total costs
- Show infrastructure failures and public health consequences with measurable outcomes
- Explain how meteorological events become economic and social crises through clear cause-effect chains
- Use accessible analogies while maintaining factual precision about timelines and scale

MEANINGFUL MEASUREMENT EXAMPLES (USE THESE TYPES):
✅ "Ocean temperatures have risen 2.3°C above seasonal averages."
✅ "Glaciers are retreating at 45 meters per year, triple the historical rate."  
✅ "The city experienced 18 centimeters of rain in 6 hours, overwhelming drainage systems."
✅ "Wildfire season now lasts 78 days longer than it did decades ago."
✅ "Crop yields have fallen 28% due to drought conditions this growing season."
✅ "Farmers report $3.2 billion in crop losses this year alone, forcing migration of nearly 120,000 individuals to urban areas."
❌ NEVER: "Water levels dropped to 11.2 units" 
❌ NEVER: "In 2023, temperatures reached record highs" (use "This year, temperatures reached record highs")

RGB COLOR RULES (DARK RANGES ONLY):
- Heat/warning: R=120-160, G=40-80, B=20-50
- Cold/data: R=10-50, G=50-90, B=100-140
- Neutral/analysis: R=50-80, G=50-80, B=50-90
- Growth data: R=20-60, G=70-110, B=30-70
- Earth data: R=90-130, G=60-100, B=30-60

IMPORTANT:
- Do NOT merge sentences into paragraphs.
- Do NOT combine multiple sentences on one line.
- Every FULL STOP (period) MUST produce a NEW LINE.
- Use ONLY concrete, understandable measurements that tell a clear story.
- NEVER reference specific calendar years.

Write the full analysis now, line-by-line, following every rule above.
"""

    return prompt


def ask_openai(prompt):
    url = "https://api.ai.it.cornell.edu/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "openai.gpt-4o",
        "messages": [
            {"role": "system", "content": "You write rich, connected climate narratives that flow naturally from one landscape to another. Never use headers or section titles."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 1.0,
        "max_tokens": 2500
    }

    r = requests.post(url, headers=headers, json=body)
    if r.status_code != 200:
        print("❌ STORY GPT ERROR:", r.status_code, r.text)
        return None
    
    return r.json()["choices"][0]["message"]["content"]


def openai_tts(text, voice, speed=1.15):
    """
    TTS with adjustable speed (1.15 = 15% faster)
    """
    url = "https://api.ai.it.cornell.edu/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    # Add speed instruction to the text
    speed_instruction = f"[Speak at {speed}x speed] " if speed != 1.0 else ""

    body = {
        "model": "openai.gpt-4o-audio-preview",
        "modalities": ["text", "audio"],
        "audio": { 
            "voice": voice, 
            "format": "wav"
        },
        "messages": [
            { "role": "system", "content": f"Convert text to expressive narration at {speed}x normal speaking speed. Maintain clarity and emotion." },
            { "role": "user", "content": speed_instruction + text }
        ]
    }

    r = requests.post(url, headers=headers, json=body)

    if r.status_code != 200:
        print("❌ TTS ERROR:", r.status_code, r.text)
        return None

    try:
        base64_audio = r.json()["choices"][0]["message"]["audio"]["data"]
    except Exception as e:
        print("❌ Error parsing audio:", e)
        return None

    import base64
    audio_bytes = base64.b64decode(base64_audio)

    out_path = Path("tts_output.wav")
    out_path.write_bytes(audio_bytes)
    return str(out_path)


def mac_say(text):
    path = "tts_output.wav"
    # Use Chinese voice for Chinese text
    if STORY_LANGUAGE == "Chinese":
        subprocess.run(["say", "-v", "Ting-Ting", "-r", "200", "-o", path, text])
    else:
        subprocess.run(["say", "-r", "200", "-o", path, text])
    return path


def play_audio(file):
    if sys.platform.startswith("darwin"):
        subprocess.run(["afplay", file])
    else:
        subprocess.run(["mpg123", file])


def parse_story(raw_story):
    import re
    pattern = r'(.*?)\[LANDSCAPE=(.*?)\]\[R=(\d+),G=(\d+),B=(\d+)\]'

    items = []
    matches = re.finditer(pattern, raw_story, re.DOTALL)
    
    for match in matches:
        text = match.group(1).strip()
        landscape = match.group(2).strip()
        r = int(match.group(3))
        g = int(match.group(4))
        b = int(match.group(5))
        
        # Skip empty text or headers
        if text and not text.startswith('#') and len(text) > 10:
            # Remove any remaining markdown or header artifacts
            text = text.replace('#', '').strip()
            items.append({
                "text": text,
                "landscape": landscape,
                "rgb": [r, g, b]
            })

    return items


def main():
    ser = None
    buffer = ""
    
    if not USE_MOCK_DATA:
        port = pick_port()
        print(f"🔌 Opening serial: {port} @ {BAUD}")
        ser = serial.Serial(port, BAUD, timeout=0.2)
        print("🌱 StoryBox ready—requesting sensor data.")
    else:
        print("🧪 Running in MOCK DATA mode (no Arduino needed)")

    # Get environment
    if USE_MOCK_DATA:
        env = get_mock_environment()
        print("📡 Mock environment generated:", env)
    else:
        ser.write(b"MEASURE\n")
        env = None

        while True:
            chunk = ser.read(1024)
            if not chunk:
                continue

            buffer += chunk.decode("utf-8", errors="ignore")

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()

                if line.startswith("ENV|"):
                    env = {}
                    for part in line.replace("ENV|", "").split("|"):
                        k, v = part.split("=")
                        env[k] = float(v)
                    print("📡 Environment received:", env)
                    break

            if env:
                break

    # Generate story
    story_type = choose_story_type()
    voice = choose_voice(story_type)

    print(f"📚 Story Type: {story_type}")
    print(f"🎤 Voice: {voice}")

    prompt = build_prompt(env, story_type)
    print("🧠 Sending to GPT via Cornell proxy...")

    raw_story = ask_openai(prompt)
    if not raw_story:
        print("❌ Failed to get story.")
        return

    story = parse_story(raw_story)
    print(f"📖 Story contains {len(story)} lines across 7 landscapes.")

    # Playback
    for idx, line in enumerate(story):
        text = line["text"]
        rgb = line["rgb"]
        landscape = line["landscape"]
        R, G, B = rgb

        # LED update
        if ser:
            ser.write(f"COLOR|{R},{G},{B}\n".encode())

        # Write JSON for webpage
        if OUTPUT_MODE in ("DISPLAY", "COMBINED"):
            write_web_json(idx, text, landscape, rgb)
            print(f"✍️  Line {idx+1}: {landscape} - {text[:60]}...")

        # TTS with faster speed
        if OUTPUT_MODE in ("SPOKEN", "COMBINED"):
            if TTS_MODE == "openai":
                audio_file = openai_tts(text, voice, speed=1.15)  # 15% faster
            else:
                audio_file = mac_say(text)  # Already set to faster rate
            if audio_file:
                play_audio(audio_file)

        time.sleep(2.0)  # Reduced to 2 seconds between sentences

    print("🌍 Story complete.")


if __name__ == "__main__":
    main()
