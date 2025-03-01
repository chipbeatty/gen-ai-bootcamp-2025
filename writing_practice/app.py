import os
import yaml
import json
import random
import streamlit as st
from dotenv import load_dotenv
import pytesseract
from PIL import Image
import requests
from gtts import gTTS
import tempfile
import base64

# Load environment variables
load_dotenv(dotenv_path='.env')

# Get API key
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    st.error('OpenAI API key not found. Please check your .env file.')
    st.stop()

# Initialize OpenAI client
import openai
openai.api_key = api_key

# Function to generate audio for French text
def generate_audio(text):
    tts = gTTS(text=text, lang='fr')
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
        tts.save(fp.name)
        return fp.name

# Function to create an HTML audio player
def get_audio_player(audio_path):
    audio_file = open(audio_path, 'rb')
    audio_bytes = audio_file.read()
    audio_base64 = base64.b64encode(audio_bytes).decode()
    audio_file.close()
    os.unlink(audio_path)  # Delete the temporary file
    return f'<audio controls><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
openai.api_base = "https://api.openai.com/v1"
openai.api_key = api_key

# Load prompts
with open('prompts.yaml', 'r') as f:
    prompts = yaml.safe_load(f)

def fetch_words():
    """Load words from local YAML file"""
    try:
        with open('words.yaml', 'r') as f:
            data = yaml.safe_load(f)
            return [{
                "french_word": word["french"],
                "english_translation": word["english"]
            } for word in data["words"]]
    except Exception as e:
        return []

def generate_sentence():
    """Generate a new practice sentence"""
    words = fetch_words()
    if not words:
        return "Error: No words available. Please check words.yaml file."
        
    word = random.choice(words)
    
    # Generate sentence using OpenAI
    prompt = prompts['sentence_generator'].replace('{{word}}', word['english_translation'])
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message['content'].strip()

def grade_submission(image, sentence):
    """Grade the submitted image"""
    if not sentence:
        return "Please generate a sentence first."
        
    # Transcribe French text from image using Tesseract
    try:
        french_text = pytesseract.image_to_string(image, lang='fra')
        french_text = french_text.strip()
        
        if not french_text:
            return "Could not read the text from the image. Please make sure the writing is clear and try again."
    except Exception as e:
        return f"Error reading image: {str(e)}"
    
    # Get literal translation
    translation_prompt = f"Translate this French text to English literally: {french_text}"
    translation_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": translation_prompt}],
        temperature=0
    )
    literal_translation = translation_response.choices[0].message['content'].strip()
    
    # Grade the submission
    grading_prompt = prompts['translation_grader']\
        .replace('{{english}}', sentence)\
        .replace('{{french}}', french_text)\
        .replace('{{translation}}', literal_translation)
        
    grading_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": grading_prompt}],
        temperature=0
    )
    
    try:
        grading_result = json.loads(grading_response.choices[0].message.content)
        return f"Your French: {french_text}\n\nTranslation: {literal_translation}\n\nGrade: {grading_result['grade']}\n\nFeedback: {grading_result['explanation']}\n\nSuggestions: {grading_result['suggestions']}"
    except json.JSONDecodeError:
        return "Error processing grading response"

# Main Streamlit app
st.set_page_config(page_title="French Writing Practice", page_icon="✍️")
st.title("French Writing Practice")

# Initialize session state
if 'current_french_sentence' not in st.session_state:
    st.session_state.current_french_sentence = ""

# Create tabs for different practice modes
tab1, tab2 = st.tabs(["Writing Practice", "Listening Practice"])

with tab1:
    # Writing Practice Tab
    if st.button("Generate New English Sentence"):
        st.session_state.current_sentence = generate_sentence()

    if st.session_state.get('current_sentence'):
        st.write("### Translate this sentence to French:")
        st.info(st.session_state.current_sentence)

    st.write("### Upload your handwritten French translation:")
    image_file = st.file_uploader("Choose an image", type=['png', 'jpg', 'jpeg'])

with tab2:
    # Listening Practice Tab
    if 'current_french_sentence' not in st.session_state:
        st.session_state.current_french_sentence = ""
        
    if st.button("Generate New French Audio"):
        # Generate a simple French sentence using OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": "Generate a simple French sentence that a beginner would understand. Only return the French sentence, nothing else."
            }],
            temperature=0.7
        )
        st.session_state.current_french_sentence = response.choices[0].message['content'].strip()
        
        # Generate and display audio
        if st.session_state.current_french_sentence:
            audio_path = generate_audio(st.session_state.current_french_sentence)
            st.markdown(get_audio_player(audio_path), unsafe_allow_html=True)
            
    # Text input for user's transcription
    user_transcription = st.text_input("Type what you hear:")
    
    if user_transcription and st.button("Check Answer"):
        # Compare with the correct sentence
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": f"Compare these two French sentences and tell me if they match in meaning (ignore minor spelling/accent mistakes):\n1. {st.session_state.current_french_sentence}\n2. {user_transcription}\n\nOnly respond with 'Correct!' if they match, or explain the difference if they don't match."
            }],
            temperature=0
        )
        feedback = response.choices[0].message['content'].strip()
        if feedback == "Correct!":
            st.success(feedback)
        else:
            st.error(feedback)
            st.info(f"The correct sentence was: {st.session_state.current_french_sentence}")

# Submit button and feedback
if image_file and st.button("Submit for Review"):
    with st.spinner("Grading your submission..."):
        try:
            # Save the uploaded file to a temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                tmp_file.write(image_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Open the temporary file with PIL
            image = Image.open(tmp_file_path)
            result = grade_submission(image, st.session_state.current_sentence)
            st.write(result)
            
            # Clean up
            import os
            os.unlink(tmp_file_path)
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")

# Instructions
with st.sidebar:
    st.write("### Instructions")
    st.write("""
    1. Click 'Generate New Sentence' to get an English sentence
    2. Write the French translation by hand
    3. Take a photo or scan your writing
    4. Upload the image
    5. Click 'Submit for Review' to get feedback
    
    Tips:
    - Write clearly and legibly
    - Pay attention to accents and punctuation
    - Review the feedback to improve your writing
    """)
