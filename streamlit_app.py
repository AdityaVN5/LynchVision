import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import io

# --- 1. CONFIGURATION & CUSTOM STYLING ---
st.set_page_config(
    page_title="LynchVision | AI Storyboarder",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme state
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# Theme toggle in sidebar
with st.sidebar:
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🌓" if st.session_state.theme == "dark" else "☀️", key="theme_toggle", help="Toggle theme"):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()

# Determine theme colors
theme = st.session_state.theme
if theme == "dark":
    bg_color = "#0e1117"
    text_color = "#ffffff"
    input_bg = "#262730"
    input_border = "#41444e"
    secondary_text = "#b1bac4"
else:
    bg_color = "#f8f9fa"
    text_color = "#1f2937"
    input_bg = "#ffffff"
    input_border = "#d1d5db"
    secondary_text = "#6b7280"

# Custom CSS for "World Class" UI
st.markdown(f"""
<style>
    /* Main Background & Fonts */
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    h1, h2, h3 {{
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        color: {text_color};
    }}
    p {{
        color: {secondary_text};
    }}
    
    /* Custom Button Styling */
    .stButton > button {{
        background: linear-gradient(135deg, #FF6B35 0%, #FF914D 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.3) !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(255, 107, 53, 0.5) !important;
        background: linear-gradient(135deg, #FF5722 0%, #FF8C42 100%) !important;
    }}
    .stButton > button > * {{
        color: #FFFFFF !important;
    }}
    .stButton > button p {{
        color: #FFFFFF !important;
        margin: 0 !important;
    }}
    .stButton > button span {{
        color: #FFFFFF !important;
    }}
    
    /* Input Fields */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {{
        background-color: {input_bg};
        color: {text_color};
        border-radius: 8px;
        border: 1px solid {input_border};
    }}
    
    /* Image Container styling */
    .css-1v0mbdj.e115fcil1 {{
        border: 1px solid {input_border};
        border-radius: 10px;
        padding: 10px;
    }}
    
    /* Status Messages */
    .stSuccess {{
        background-color: rgba(28, 131, 225, 0.1);
        border-left: 5px solid #1c83e1;
    }}
</style>
""", unsafe_allow_html=True)

# --- 2. LOGIC FUNCTIONS ---

def get_gemini_client(api_key):
    return genai.Client(api_key=api_key)

def generate_director_prompt(client, ref_img, user_scene_context):
    """
    Uses Gemini 2.5 Flash to analyze the image and user context to write a technical prompt.
    """
    base_instruction = """
    You are an expert film director. Look at the character in this image.
    I need a prompt for an AI Image Generator to create a '3x3 Cinematic Storyboard Sheet' (9 panels total).

    The prompt must:
    1. Describe a consistent scene (e.g., an intense action chase in a dusty market).
    2. Specify the layout: "A 3x3 grid contact sheet".
    3. Describe 9 distinct camera angles (Wide, Over-the-shoulder, Extreme Close-up of eyes, Low angle, etc.).
    4. Mention specific details from the reference image (e.g., "man with beard", "white shirt") to reinforce consistency.
    5. Style keywords: "Cinematic lighting, 4k, teal and orange, motion blur, highly detailed".

    Output ONLY the final prompt text. Do not add conversational filler.
    """
    
    context_instruction = f"""
    The user wants this specific scene/context: "{user_scene_context}"
    """ if user_scene_context else "A dynamic, high-energy cinematic moment with professional production value"

    final_instruction = f"""
    {base_instruction}
    {context_instruction}

    REQUIREMENTS:
    1. Describe the scene vividly (lighting, atmosphere, background).
    2. Maintain the character's key features from the image (hair, clothes, vibe).
    3. Use high-end keywords: "8k, cinematic lighting, photorealistic, depth of field".
    
    Output ONLY the final prompt text. No "Here is the prompt" text.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[ref_img, final_instruction]
        )
        return response.text
    except Exception as e:
        st.error(f"Director Error: {e}")
        return None

def generate_image(client, prompt_text, ref_img, aspect_ratio):
    """
    Uses Gemini 3 Pro Image Preview to generate the final visual.
    """
    try:
        # Map UI aspect ratio to API strings if needed, or pass directly
        # API accepts: "1:1", "16:9", "4:3", etc.
        
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=[prompt_text, ref_img],
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE'],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size="2K"
                ),
            )
        )
        
        from PIL import Image as PILImage
        
        # Try different approaches to extract image bytes from response
        for part in response.parts:
            try:
                # Method 1: Check if part has inline_data with image bytes
                if hasattr(part, 'inline_data') and part.inline_data:
                    image_bytes = part.inline_data.data
                    return PILImage.open(io.BytesIO(image_bytes))
            except:
                pass
            
            try:
                # Method 2: Try as_image() and extract from that
                if part.as_image():
                    image_obj = part.as_image()
                    
                    # Try different attributes
                    if hasattr(image_obj, 'data'):
                        return PILImage.open(io.BytesIO(image_obj.data))
                    elif hasattr(image_obj, '_image_bytes'):
                        return PILImage.open(io.BytesIO(image_obj._image_bytes))
                    elif hasattr(image_obj, 'mime_type'):
                        # It's an image object, try to access its data
                        if hasattr(image_obj, '__dict__'):
                            for key, value in image_obj.__dict__.items():
                                if isinstance(value, bytes) and len(value) > 100:
                                    return PILImage.open(io.BytesIO(value))
            except:
                pass
        
        st.error("❌ Could not extract image data from response. The API response format may have changed.")
        return None
        
    except Exception as e:
        st.error(f"Cinematographer Error: {str(e)}")
        return None

# --- 3. UI LAYOUT ---

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    api_key = st.text_input("Google API Key", type="password", help="Get yours at aistudio.google.com")
    
    st.markdown("---")
    st.markdown("""
    ### 📝 How it works
    1. **Upload** a character reference.
    2. **Describe** the scene (optional).
    3. **Generate** a perfectly consistent cinematic shot.
    """)
    st.info(":blue[Powered by Gemini 3 Pro (Vision)]")

# Main Header
st.title("🎬 LynchVision")
st.markdown("#### Turn character references into cinematic shots instantly.(One Shot Reference)")
st.markdown("Transform your images into stunning cinematic storyboards. Upload a reference image and watch as our system generates a beautiful 3x3 grid of keyframes that bring your vision to life.")
st.markdown("Use your Google API Key with Gemini 3 Pro enabled to get started!")
st.markdown("---")

# Layout: Two Columns
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.subheader("1. Input")
    
    uploaded_file = st.file_uploader("Upload Reference Image(Single)", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        # Display uploaded image
        ref_image = Image.open(uploaded_file)
        st.image(ref_image, caption="Reference Character", width=300)
    
    st.markdown("### Scene Details")
    scene_prompt = st.text_area(
        "Scene Context (Optional)", 
        placeholder="e.g., Standing on a rainy rooftop at night, neon lights in background, holding a futuristic device...",
        height=100
    )
    
    # Dropdown for default scene info
    with st.expander("ℹ️ What's the Default Scene?"):
        st.markdown("""
        **If you leave Scene Context empty, the AI will generate:**
        
        - 🎬 **Scene**: A cinematic moment featuring intense action, drama, or storytelling
        - 💡 **Lighting**: Dramatic studio lighting with volumetric effects and rim lighting
        - 🎨 **Color**: Cinematic palette with teal/orange, rich contrast and saturation
        - 📷 **Camera**: Professional framing with shallow depth of field and bokeh
        - 🌆 **Atmosphere**: Immersive, visually compelling environment
        - ⚡ **Motion**: Dynamic energy with suggestion of movement or tension
        - ✨ **Quality**: Award-winning cinematography, premium visual aesthetic
        
        **Pro Tip:** Add your own context for more control (e.g., location, mood, lighting preference, action).
        """)
    
    aspect_ratio = st.selectbox(
        "Aspect Ratio",
        options=["1:1", "16:9", "9:16", "4:3", "3:4"],
        index=0
    )
    
    generate_btn = st.button("✨ Generate Cinematic Shot")

with col2:
    st.subheader("2. Result")
    
    # Placeholder for dynamic content
    result_container = st.container()
    
    if generate_btn:
        if not api_key:
            st.warning("⚠️ Please enter your Google API Key in the sidebar.")
        elif not uploaded_file:
            st.warning("⚠️ Please upload a reference image.")
        else:
            client = get_gemini_client(api_key)
            
            with st.status("🎬 Production in progress...", expanded=True) as status:
                
                # Step 1: Director
                status.write("🧠 The Director is writing the prompt...")
                generated_prompt = generate_director_prompt(client, ref_image, scene_prompt)
                
                if generated_prompt:
                    status.write("📝 Prompt created. Sending to Cinematographer...")
                    with st.expander("View Generated Prompt"):
                        st.code(generated_prompt, language="text")
                    
                    # Step 2: Cinematographer
                    status.write("🎨 Rendering image with Gemini 3 Pro...")
                    final_image = generate_image(client, generated_prompt, ref_image, aspect_ratio)
                    
                    if final_image:
                        status.update(label="✅ Production Complete!", state="complete", expanded=False)
                        
                        # Dynamic Layout Display
                        # Adjust width based on aspect ratio for better presentation
                        width_setting = "auto"
                        if aspect_ratio == "9:16":
                            # Constrain width so tall images don't take up too much vertical scrolling space
                            st.image(final_image, caption="Generated Shot", width=350) 
                        else:
                            st.image(final_image, caption="Generated Shot", use_container_width=True)
                        
                        # Download Button - only for PIL Images
                        try:
                            from PIL import Image as PILImage
                            if isinstance(final_image, PILImage.Image):
                                buf = io.BytesIO()
                                final_image.save(buf, format="PNG")
                                byte_im = buf.getvalue()
                                
                                st.download_button(
                                    label="⬇️ Download Image",
                                    data=byte_im,
                                    file_name="cinegen_output.png",
                                    mime="image/png"
                                )
                        except Exception as e:
                            st.warning(f"Could not create download button: {e}")
                    else:
                        status.update(label="❌ Rendering Failed", state="error")
                else:
                    status.update(label="❌ Prompt Generation Failed", state="error")
