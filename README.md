# 🌍 StoryBox: Interactive Climate Storytelling Installation

**StoryBox** is an immersive, AI-powered installation that transforms environmental data into personalized climate narratives. Users become "gods" of a miniature world, manipulating physical conditions (temperature, humidity, wind, water) and witnessing how their actions cascade through seven interconnected landscapes through real-time storytelling, dynamic visuals, and ambient lighting.

![StoryBox Demo](assets/demo.gif) <!-- Add your demo gif here -->

## ✨ Features

- 🎭 **Dual Narrative Modes**: Emotional storytelling or data-driven analysis
- 🌐 **Multi-Sensory Output**: Visual display, audio narration, and synchronized LED lighting
- 🔄 **Real-Time Response**: Stories adapt instantly to environmental changes
- 🎨 **Dynamic Visuals**: Background colors and animations match story content
- 🌊 **Seven Interconnected Landscapes**: Ocean, countryside, city, glacier, mountain, forest, desert
- 🤖 **AI-Powered**: GPT-4 generates unique, contextual narratives
- 🎤 **Voice Narration**: OpenAI TTS with multiple voice options

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Physical Interaction                      │
│        (User manipulates: mist, heat, wind, water)          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Hardware Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  DHT11   │  │Ultrasonic│  │   Wind   │  │ LED Strip│   │
│  │ (Temp/H) │  │ (Water)  │  │  Sensor  │  │ (WS2812) │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Arduino Uno R4 WiFi                             │
│        Serial Communication (115200 baud)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               Python Processing Layer                        │
│  • Sensor data parsing                                       │
│  • GPT-4 story generation                                    │
│  • OpenAI TTS (text-to-speech)                              │
│  • LED color control                                         │
│  • JSON output for web interface                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 Presentation Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Web Display  │  │ Audio Output │  │ LED Ambient  │     │
│  │  (Canvas)    │  │   (TTS)      │  │   Lighting   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Hardware Requirements

### Components
- **Arduino Uno R4 WiFi**
- **DHT11** Temperature & Humidity Sensor
- **HC-SR04** Ultrasonic Distance Sensor (for water level)
- **Modern Device Wind Sensor Rev C**
- **WS2812B LED Strip** (20 LEDs recommended)
- **5V Power Supply** for LED strip
- Jumper wires and breadboard

### Wiring Diagram
```
DHT11:
  - VCC → 5V
  - GND → GND
  - DATA → Pin 2

Ultrasonic Sensor:
  - VCC → 5V
  - GND → GND
  - TRIG → Pin 9
  - ECHO → Pin 10

Wind Sensor:
  - VCC → 5V
  - GND → GND
  - RV → A1
  - TMP → A0

LED Strip:
  - VCC → External 5V Power Supply
  - GND → GND (shared with Arduino)
  - DATA → Pin 6
```

## 💻 Software Requirements

### System Requirements
- **Python 3.7+**
- **macOS** or **Linux** (Windows requires mpg123 for audio)
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

### Python Dependencies
```bash
pip install pyserial requests
```

### API Requirements
- **OpenAI API Key** (Cornell proxy supported)
- Access to `api.ai.it.cornell.edu` or `api.openai.com`

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/storybox.git
cd storybox
```

### 2. Upload Arduino Code
1. Open `arduino/storybox_sensors.ino` in Arduino IDE
2. Select **Arduino Uno R4 WiFi** as your board
3. Upload to your Arduino
4. Close Arduino IDE (Serial Monitor must be closed!)

### 3. Configure Python Script
Edit `storybox_output.py`:
```python
# Line 13: Add your API key
OPENAI_API_KEY = "your-api-key-here"

# Line 11: Set to False when using real Arduino
USE_MOCK_DATA = False

# Line 14: Choose mode
STORY_TYPE_MODE = "RANDOM"  # or "EMOTIONAL" or "DATA"

# Line 15: Choose output
OUTPUT_MODE = "COMBINED"  # or "SPOKEN" or "DISPLAY"
```

### 4. Start Web Server
```bash
cd storybox
python3 -m http.server 8000
```

### 5. Run the System
Open a new terminal:
```bash
python3 storybox_output.py
```

Open browser to: **http://localhost:8000/index.html**

## 🎮 Usage

### User Interaction Flow
1. **Manipulate the Environment**
   - Spray mist (increases humidity)
   - Use hair dryer (increases temperature)
   - Use fan (increases wind)
   - Pour water (increases water level)

2. **Sensors Detect Changes**
   - Arduino reads all sensors in real-time
   - Data sent to Python via serial

3. **AI Generates Story**
   - GPT-4 creates personalized narrative
   - Connects all 7 landscapes
   - Includes color suggestions

4. **Multi-Sensory Output**
   - **Visual**: Animated background with story text
   - **Audio**: AI voice narrates the story
   - **Light**: LEDs change color to match narrative

### Story Modes

#### 🎭 Emotional Mode
- Poetic, sensory-rich descriptions
- Focus on human and biological impact
- Atmospheric and evocative language
- Voices: fable, nova, ballad, meadow, clover

#### 📊 Data-Driven Mode
- Analytical environmental reports
- Concrete measurements and statistics
- Accessible scientific explanations
- Voices: alloy, echo, coral, verse, onyx

## 📁 Project Structure

```
storybox/
├── storybox_output.py          # Main Python script
├── arduino/
│   └── storybox_sensors.ino    # Arduino sensor code
├── web/
│   ├── index.html              # Web interface
│   ├── style.css               # Styling
│   ├── script.js               # Main logic
│   └── canvas.js               # Background animation
├── story.json                  # Real-time story data
├── assets/
│   └── storybox_logo.png       # Logo
└── README.md                   # This file
```

## 🎨 Customization

### Change Story Language
Currently English only. Other languages require:
1. Set `STORY_LANGUAGE` in Python (line 21)
2. For Chinese: Use `TTS_MODE = "macsay"` (Mac only)
3. OpenAI TTS only supports English

### Adjust Timing
```python
# Line 420: Time between sentences
time.sleep(2.0)  # Increase for slower pacing
```

### Modify LED Count
```cpp
// arduino/storybox_sensors.ino, line 8
#define LED_COUNT 20  // Change to your LED count
```

### Add Custom Surprising Causes
Edit `surprising_causes` list in `build_prompt()` function (line 84)

## 🐛 Troubleshooting

### Arduino Issues
**"Resource busy" error:**
- Close Arduino Serial Monitor
- Disconnect and reconnect Arduino
- Try: `sudo pkill -f "usbmodem"`

**LEDs not changing:**
- Check LED power supply (needs external 5V)
- Verify data wire on Pin 6
- Test with Arduino Serial Monitor: `COLOR|255,0,0`

### Python Issues
**"No serial ports found":**
- Arduino not connected or not recognized
- Check USB cable and port
- On Mac: Install serial drivers if needed

**GPT API errors:**
- Check API key is correct
- Verify Cornell proxy access
- Check internet connection

### Web Interface Issues
**Story not updating:**
- Check `story.json` exists and updates
- Browser console (F12) for errors
- Ensure web server is running on port 8000

**Auto-scroll not working:**
- Clear browser cache
- Check console for JavaScript errors

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT-4 and TTS APIs
- **Cornell University** for API proxy access
- **Adafruit** for NeoPixel library
- Climate scientists and storytellers who inspire this work

## 📧 Contact

**Project Creator**: [Your Name]
- Email: your.email@example.com
- GitHub: [@yourusername](https://github.com/yourusername)

## 🌟 Demo & Media

[Add links to:]
- Video demo
- Live installation photos
- User testimonials
- Conference presentations

---

**Built with ❤️ for climate awareness and interactive storytelling**
