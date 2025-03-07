import streamlit as st
import json
import os
from dotenv import load_dotenv
import openai

# Set page config and styling
st.set_page_config(page_title="French Vocabulary Importer", layout="wide")

# Custom CSS to make the container wider and add text wrapping
st.markdown('''
<style>
    .block-container {max-width: 95% !important; padding: 1rem 5rem !important;}
    .stCodeBlock {white-space: pre-wrap !important;}
</style>''', unsafe_allow_html=True)

# Load environment variables from parent directory
load_dotenv(dotenv_path='../.env')

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_vocab(topic, num_words=10):
    """Generate French vocabulary words and definitions using OpenAI."""
    system_prompt = """You are a French language expert. Your task is to generate vocabulary words with their translations, 
    context, and pronunciation tips. You must ALWAYS respond with valid JSON in the exact format specified. 
    Double-check your JSON is properly formatted before responding. Do not include any additional text or explanations."""
    
    user_prompt = f"""Generate {num_words} French vocabulary words related to '{topic}' in this EXACT JSON format:
    {{
        "word_group": "{topic}",
        "words": [
            {{
                "french_word": "word in French",
                "part_of_speech": "e.g., noun (gender), verb (infinitive), adjective (m/f forms)",
                "english_translation": "English translation",
                "context": "Example sentence in French showing usage",
                "context_translation": "English translation of the context",
                "pronunciation_tips": "Brief notes on pronunciation if needed"
            }}
        ]
    }}
    
    Important instructions:
    1. For nouns: Include the gender (masculine/feminine)
    2. For verbs: Include infinitive and present tense forms
    3. For adjectives: Include masculine and feminine forms
    4. Context sentences should be natural, everyday French
    5. Include any silent letters or liaison notes in pronunciation tips
    6. Use common French vocabulary suitable for beginners to intermediate learners
    7. CRITICAL: Ensure your response is ONLY the JSON object - no additional text
    8. Verify all JSON syntax (quotes, braces, commas) is correct before responding
    """
    
    try:
        # Make API call with both system and user prompts
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1500  # Increased for larger responses
        )
        
        # Get the response content and clean it
        content = response['choices'][0]['message']['content'].strip()
        
        # Try to parse the JSON response
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            st.error("⚠️ The generated content was not valid JSON. Retrying...")
            st.error(f"Error details: {str(e)}")
            return None
            
    except Exception as e:
        st.error(f"⚠️ Error generating vocabulary: {str(e)}")
        return None

def save_vocab(vocab_data, filename):
    """Save vocabulary data to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(vocab_data, f, indent=2)

def load_vocab(file):
    """Load vocabulary data from a JSON file."""
    return json.load(file)

# Streamlit UI
st.title("French Vocabulary Importer")
st.write("Generate, import, and export French vocabulary words for your language learning app")
st.markdown("""### Features:
- Generates proper French vocabulary with gender and forms
- Includes pronunciation tips and part of speech information
- Provides natural French example sentences
- Supports everyday vocabulary for practical use
""")

# Sidebar for generation options
# Predefined topics for French learning
TOPICS = [
    "Daily Activities",
    "Food and Dining",
    "Family and Friends",
    "Travel and Transportation",
    "Home and Living",
    "Work and School",
    "Hobbies and Entertainment",
    "Weather and Seasons",
    "Shopping and Money",
    "Health and Wellness"
]

with st.sidebar:
    st.header("Vocabulary Generation")
    
    # Topic selection with explanation
    st.subheader("1. Choose a Topic")
    topic = st.selectbox(
        "Select a topic for vocabulary generation",
        options=TOPICS,
        help="Choose a topic that you want to learn vocabulary for"
    )
    
    # Custom topic option
    use_custom_topic = st.checkbox("Use custom topic instead")
    if use_custom_topic:
        topic = st.text_input("Enter your custom topic")
    word_type = st.selectbox(
        "Word Type",
        ["All", "Nouns", "Verbs", "Adjectives", "Common Phrases", "Adverbs"]
    )
    num_words = st.number_input("Number of words", min_value=5, max_value=50, value=10)
    
    if st.button("Generate Vocabulary"):
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            with st.spinner(f"Generating vocabulary (attempt {retry_count + 1}/{max_retries})..."):
                vocab_data = generate_vocab(topic, num_words)
                if vocab_data is not None:
                    st.session_state.vocab_data = vocab_data
                    st.success("✅ Vocabulary generated successfully!")
                    break
                retry_count += 1
                if retry_count < max_retries:
                    st.warning(f"Retrying... (attempt {retry_count + 1}/{max_retries})")
        
        if retry_count == max_retries and vocab_data is None:
            st.error("❌ Failed to generate valid vocabulary after multiple attempts. Please try again.")

# Main area for displaying and managing vocabulary
tab1, tab2 = st.tabs(["📝 Generate Vocabulary", "📤 Import from File"])

# Add explanation of the process
st.sidebar.markdown("""---
### How it works:
1. Select a topic or enter your own
2. Choose the type of words you want
3. Set how many words to generate
4. Click 'Generate' to create vocabulary
5. The generated words will appear on the right
6. Click 'Save to File' to download them
""")

with tab1:
    if 'vocab_data' in st.session_state:
        st.markdown("### Generated Vocabulary with Preview")
        
        # Get the words from the vocabulary data
        words = st.session_state.vocab_data.get('words', [])
        
        # Show the opening of the JSON structure
        opening_json = {
            'word_group': st.session_state.vocab_data.get('word_group', ''),
            'words': '['
        }
        st.code(json.dumps(opening_json, indent=4)[:-2] + '[', language='json')
        
        # For each word, show its JSON and preview card side by side
        for i, word in enumerate(words):
            # Make JSON column wider (ratio 3:2)
            cols = st.columns([3, 2])
            
            # Format the JSON for this word
            word_json = json.dumps(word, indent=4).split('\n')
            # Add comma for all but the last word
            if i < len(words) - 1:
                word_json[-1] += ','
            word_json = '\n'.join(word_json)
            
            with cols[0]:
                st.code(word_json, language='json')
            
            with cols[1]:
                st.markdown(f"""
                <div style='border: 1px solid #e0e0e0; padding: 1.25rem; border-radius: 0.5rem; background-color: white;'>
                    <div style='font-size: 1.1rem; font-weight: 600; color: #1a202c;'>Word: {word.get('french_word', '')}</div>
                    <div style='color: #2d3748; margin-top: 0.5rem; font-weight: 500;'>Translation: {word.get('english_translation', '')}</div>
                    <div style='color: #2d3748; margin-top: 0.5rem; font-style: italic;'>Context: {word.get('context', '')}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Show the closing of the JSON structure
        st.code('''
    ]
}''', language='json', line_numbers=False)
        
        # Export option with explanation
        st.markdown("### Save Vocabulary")
        st.markdown("Click below to save these words for use in the main application:")
        if st.button("💾 Save to File"):
            filename = f"vocab_{topic.lower().replace(' ', '_')}.json"
            save_vocab(st.session_state.vocab_data, filename)
            st.success(f"✅ Vocabulary saved to {filename}")
            st.info("This file can now be imported into the main French Vocabulary Builder application.")

with tab2:
    st.markdown("### Import Existing Vocabulary")
    st.markdown("""
    You can import vocabulary files that were:
    - Previously generated and saved
    - Shared by your teacher
    - Created for specific lessons
    """)
    
    # Import option
    uploaded_file = st.file_uploader("Select a vocabulary file", type='json')
    if uploaded_file is not None:
        vocab_data = load_vocab(uploaded_file)
        st.success("✅ File imported successfully!")
        
        # Display the vocabulary in a more readable format
        st.markdown("### Imported Vocabulary")
        for word in vocab_data.get('words', []):
            with st.expander(f"📚 {word.get('french_word', '')}"):
                st.write(f"**English:** {word.get('english_translation', '')}")
                st.write(f"*Context:* {word.get('context', '')}")
                if 'pronunciation_tips' in word:
                    st.write(f"🔊 *Pronunciation:* {word.get('pronunciation_tips', '')}")
