# 🎬 LynchVision | AI Storyboarder

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](http://lynchvision.streamlit.app/)
[![Powered by Gemini](https://img.shields.io/badge/Powered%20by-Gemini%203%20Pro-blue?logo=google-gemini)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)

**Turn single character references into consistent, cinematic 3x3 storyboards instantly.**

LynchVision is a Streamlit application that acts as your personal AI film crew. By combining a "Director" agent (for vision) and a "Cinematographer" agent (for rendering), it transforms a single reference image into a high-fidelity, production-grade storyboard sheet.

🔗 **Live Demo:** [lynchvision.streamlit.app](http://lynchvision.streamlit.app/)

---

## ☕ Why "LynchVision"?

> *"Ideas are like fish. If you want to catch little fish, you can stay in the shallow water. But if you want to catch the big fish, you’ve got to go deeper."* — David Lynch

This project is a tribute to the legendary filmmaker **David Lynch** (*Twin Peaks, Mulholland Drive, Blue Velvet*).

Lynch is known for his ability to transform the mundane into the surreal, the uncanny, and the profoundly cinematic. He doesn't just shoot scenes; he creates **atmospheres**. 

**LynchVision** aims to capture that spirit of "auteur" direction. It doesn't just copy your image; it interprets it. It adds mood, lighting, grain, and cinematic texture, turning a simple character reference into a scene that feels like it was pulled from a dream or a high-budget film set.

---

## ✨ Key Features

* **🎥 The "Director" Agent (Gemini 2.5 Flash):** Analyzes your reference image and scene context to write a highly technical, prompt-engineered script. It understands lighting, camera angles (OTB, Wide, Extreme Close-up), and visual consistency.
    
* **🎨 The "Cinematographer" Agent (Gemini 3 Pro):** Uses the latest `gemini-3-pro-image-preview` model to render the storyboard. It adheres strictly to the reference character while applying the Director's stylistic instructions.

* **🧩 3x3 Contact Sheet Layout:** Generates a professional "contact sheet" grid (9 panels) by default, allowing you to see your character in various angles and poses in a single generation.

* **📐 Aspect Ratio Control:** Support for standard cinema and social ratios: `16:9` (Cinema), `9:16` (Social), `1:1` (Square), `4:3`, and `3:4`.

* **🌑 Minimal UI:** A fully responsive, dark-mode-ready interface built with custom CSS for a premium editing experience.

---

## 🚀 How It Works

1.  **Upload Reference:** You provide a single image of a character (the "Actor").
2.  **Set Context:** (Optional) You describe the scene (e.g., *"Standing on a rainy rooftop at night"*). If you leave this blank, the Director improvises a dramatic, high-contrast scene.
3.  **Action:** * The **Director** (Gemini 2.5) looks at your image and writes a detailed prompt: *"Cinematic lighting, teal and orange palette, 3x3 grid, consistent character details..."*
    * The **Cinematographer** (Gemini 3) takes that prompt and renders the final shot.

---
## 🎞️ Example Generation

| **Reference Actor (Input)** | **Scene Context** | **Cinematic Storyboard (Output)** |
|:-------------------------:|:-----------:|:--------------------------------:|
| <img src="examples/input.jpg" width="200" /> | ➡️ Driver having an intense conversation, getting ready for the race | <img src="examples/output.png" width="500" /> |
| *Single reference image* | *Scene Prompt* | *Consistent 3x3 Contact Sheet* |
---

## 🛠️ Installation & Local Development

To run LynchVision on your local machine:

**1. Clone the repository**
```bash
git clone [https://github.com/yourusername/LynchVision.git](https://github.com/yourusername/LynchVision.git)
cd LynchVision
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Run the app**

```bash
streamlit run streamlit_app.py
```

**4. Authenticate You will need a Google API Key with access to the Gemini API.**

Get your key here: [Google AI Studio](https://aistudio.google.com/)

Enter the key in the sidebar of the app.

## 🏗️ Tech Stack
- Frontend: Streamlit (Python)
- Vision/Reasoning Model: Google Gemini 2.5 Flash
- Image Generation Model: Google Gemini 3 Pro (gemini-3-pro-image-preview)
- Image Processing: Pillow (PIL)

## 📄 License
This project is licensed under the Apache 2.0 License - see the LICENSE file for details.
