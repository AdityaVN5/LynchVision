import streamlit as st
import google.generativeai as genai
import requests
import base64
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
from io import BytesIO

# --- 1. UI CONFIGURATION (Must be first) ---
st.set_page_config(
    page_title="LynchVision",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CUSTOM CSS FOR "WORLD CLASS" MINIMAL UI ---
st.markdown("""
<style>
    /* Clean font and spacing */
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    h1 {font-weight: 700; letter-spacing: -1px;}
    p {font-size: 1.1rem; color: #555;}
    
    /* Elegant Card Styling for Images */
    .stImage {
        border-radius: 12px;
        transition: transform 0.2s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stImage:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 15px rgba(0,0,0,0.15);
    }
    
    /* Button Styling */
    div.stButton > button {
        width: 100%;
        background-color: #000 !important;
        color: white !important;
        border-radius: 8px;
        padding: 0.75rem;
        font-weight: 600;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #333 !important;
        color: white !important;
    }
    div.stButton > button * {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---

def encode_image(uploaded_file):
    """Encodes streamlit uploaded file to base64."""
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def get_shot_prompts(api_key, image_data):
    """Uses Gemini 1.5 Flash to generate 9 cinematic shot descriptions."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
    prompt = """
    You are a Director of Photography. Look at this character reference.
    Generate a Python list of exactly 9 distinct prompts for a "3x3 Cinematic Character Sheet".
    
    THE SCENE: A high-stakes action sequence in a vibrant, dusty Indian market.
    
    REQUIREMENTS:
    1. Include the character's key features (beard, hair, outfit) in EVERY prompt to ensure consistency.
    2. Vary the angles: Wide, Close-up, Low-angle, Overhead, Dutch angle, Behind-the-back, etc.
    3. Style keywords: "Cinematic lighting, 4k, teal and orange, photorealistic, motion blur".
    
    Output ONLY the raw Python list. No markdown, no "python" tag.
    Example: ["Prompt 1", "Prompt 2", ...]
    """
    
    # We need to wrap the bytes for the Gemini SDK
    cookie_picture = {
        'mime_type': 'image/jpeg',
        'data': image_data
    }
    
    try:
        response = model.generate_content([cookie_picture, prompt])
        # robust cleaning of the response
        text = response.text.strip()
        if text.startswith("```"): text = text.split("\n", 1)[1]
        if text.endswith("```"): text = text.rsplit("\n", 1)[0]
        prompts = eval(text)
        return prompts
    except Exception as e:
        st.error(f"Error generating prompts: {e}")
        return []

def generate_single_image(index, prompt, ref_b64, api_key):
    """Calls Freepik API to generate one image."""
    API_URL = "https://api.freepik.com/v1/ai/gemini-2-5-flash-image-preview"
    headers = {"x-freepik-api-key": api_key, "Content-Type": "application/json"}
    
    payload = {
        "prompt": prompt,
        "reference_images": [ref_b64],
        "num_images": 1,
        "image_size": "square_hd", # Good for grids
        "guidance_scale": 3.0,     # Strong adherence to reference
        "num_inference_steps": 25
    }

    try:
        req = requests.post(API_URL, json=payload, headers=headers)
        if req.status_code != 200:
            return index, None
            
        task_id = req.json()["data"]["task_id"]
        
        # Polling loop (max 60s)
        for _ in range(30):
            time.sleep(2)
            status_req = requests.get(f"{API_URL}/{task_id}", headers=headers)
            if status_req.json()["data"]["status"] == "COMPLETED":
                img_url = status_req.json()["data"]["generated"][0]
                img_data = requests.get(img_url).content
                return index, img_data
        
        return index, None
    except:
        return index, None

# --- 4. MAIN APP LOGIC ---

# Sidebar for Keys
with st.sidebar:
    st.header("🔑 API Keys")
    st.markdown("Enter your keys to start.")
    google_key = st.text_input("Google Gemini API Key", type="password")
    freepik_key = st.text_input("Freepik API Key", type="password")
    st.divider()
    st.info("Get keys from Google AI Studio and Freepik Developer Portal.")

# Main Content
st.title("🎬 LynchVision")
st.markdown("Generate consistent **3x3 Cinematic Storyboards** from a single character photo.")

uploaded_file = st.file_uploader("Upload Character Reference", type=['jpg', 'png', 'jpeg'])

if uploaded_file and google_key and freepik_key:
    # Display reference in a small expander
    with st.expander("View Reference Image", expanded=False):
        st.image(uploaded_file, width=500, caption="Character Reference")

    if st.button("Generate Storyboard"):
        
        # 1. Setup
        ref_bytes = uploaded_file.getvalue()
        ref_b64 = base64.b64encode(ref_bytes).decode('utf-8')
        
        # 2. Get Prompts
        with st.status("🧠 Analyzing character & writing script...", expanded=True) as status:
            prompts = get_shot_prompts(google_key, ref_bytes)
            
            if not prompts:
                status.update(label="Error generating prompts", state="error")
                st.stop()
                
            status.write(f"✅ Generated {len(prompts)} distinct shot descriptions.")
            
            # 3. Concurrent Image Generation
            status.write("🎨 Generating 9 images concurrently...")
            progress_bar = st.progress(0)
            
            # Placeholder for results in session state to preserve order
            results = [None] * 9
            completed_count = 0
            
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [
                    executor.submit(generate_single_image, i, p, ref_b64, freepik_key) 
                    for i, p in enumerate(prompts)
                ]
                
                for future in as_completed(futures):
                    idx, img_bytes = future.result()
                    if img_bytes:
                        results[idx] = img_bytes
                    completed_count += 1
                    progress_bar.progress(completed_count / 9)
            
            status.update(label="All shots completed!", state="complete", expanded=False)

        # 4. Store in Session State (prevents loss on rerun)
        st.session_state['generated_grid'] = results

# --- 5. GRID DISPLAY ---
if 'generated_grid' in st.session_state:
    st.divider()
    st.subheader("Your Storyboard")
    
    grid_images = st.session_state['generated_grid']
    
    # 3x3 Dynamic Grid Layout
    # We loop through rows (0, 3, 6)
    for i in range(0, 9, 3):
        cols = st.columns(3) # Create 3 columns
        for j in range(3):
            img_data = grid_images[i+j]
            with cols[j]:
                if img_data:
                    # Convert bytes to PIL Image for display
                    image = Image.open(BytesIO(img_data))
                    st.image(image, use_container_width=True)
                    
                    # Optional: Add download button for each
                    st.download_button(
                        label="⬇️",
                        data=img_data,
                        file_name=f"shot_{i+j+1}.jpg",
                        mime="image/jpeg",
                        key=f"btn_{i+j}"
                    )
                else:
                    st.error("Generation Failed")

elif not uploaded_file:
    st.markdown("---")
    st.markdown("👆 *Upload an image above to begin.*")