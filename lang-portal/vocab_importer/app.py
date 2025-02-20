import streamlit as st
import json
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_vocab(topic, num_words=10):
    """Generate Latin vocabulary words and definitions using OpenAI."""
    prompt = f"""Generate {num_words} Latin vocabulary words related to '{topic}' in the following JSON format:
    {{
        "word_group": "{topic}",
        "words": [
            {{
                "word": "latin_word",
                "part_of_speech": "e.g., noun (genitive form), verb (principal parts), adjective (declension)",
                "definition": "English definition",
                "example_sentence": "Latin example sentence",
                "example_translation": "English translation of the example"
            }}
        ]
    }}
    
    Important instructions:
    1. For nouns: Include the nominative and genitive forms
    2. For verbs: Include all four principal parts
    3. For adjectives: Include masculine, feminine, and neuter forms
    4. Example sentences should be classical Latin usage
    5. Ensure all macrons are marked where appropriate
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return json.loads(response.choices[0].message.content)

def save_vocab(vocab_data, filename):
    """Save vocabulary data to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(vocab_data, f, indent=2)

def load_vocab(file):
    """Load vocabulary data from a JSON file."""
    return json.load(file)

# Streamlit UI
st.title("Latin Vocabulary Importer")
st.write("Generate, import, and export Latin vocabulary words for your language learning app")
st.markdown("""### Features:
- Generates proper Latin vocabulary with all necessary forms
- Includes part of speech information
- Provides classical Latin example sentences
- Marks macrons for proper pronunciation
""")

# Sidebar for generation options
with st.sidebar:
    st.header("Generation Options")
    topic = st.text_input("Topic/Theme", "Roman Family Terms")
    word_type = st.selectbox(
        "Word Type",
        ["All", "Nouns", "Verbs", "Adjectives", "Adverbs", "Prepositions"]
    )
    num_words = st.number_input("Number of words", min_value=5, max_value=50, value=10)
    
    if st.button("Generate Vocabulary"):
        with st.spinner("Generating vocabulary..."):
            vocab_data = generate_vocab(topic, num_words)
            st.session_state.vocab_data = vocab_data
            st.success("Vocabulary generated!")

# Main area for displaying and managing vocabulary
tab1, tab2 = st.tabs(["Generate & Export", "Import"])

with tab1:
    if 'vocab_data' in st.session_state:
        st.json(st.session_state.vocab_data)
        
        # Export option
        if st.button("Export to JSON"):
            filename = f"vocab_{topic.lower().replace(' ', '_')}.json"
            save_vocab(st.session_state.vocab_data, filename)
            st.success(f"Saved to {filename}")

with tab2:
    # Import option
    uploaded_file = st.file_uploader("Choose a JSON file", type='json')
    if uploaded_file is not None:
        vocab_data = load_vocab(uploaded_file)
        st.json(vocab_data)
        st.success("File imported successfully!")
