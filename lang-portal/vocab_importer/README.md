# Latin Vocab Importer

A Streamlit-based tool specifically designed for generating, importing, and exporting Latin vocabulary words for language learning applications. This tool ensures proper Latin word forms, includes grammatical information, and provides classical Latin examples.

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Features

- Generate Latin vocabulary with proper grammatical forms:
  - Nouns: Nominative and genitive forms
  - Verbs: All four principal parts
  - Adjectives: Masculine, feminine, and neuter forms
- Include part of speech information and grammatical details
- Provide classical Latin example sentences with translations
- Mark macrons for proper pronunciation
- Export generated vocabulary to JSON files
- Import existing vocabulary from JSON files
- Filter by word types (Nouns, Verbs, Adjectives, etc.)
- Customizable number of words and topics

## Usage

1. Enter a Latin-related topic (e.g., "Roman Family Terms", "Military Vocabulary")
2. Select the desired word type (Nouns, Verbs, Adjectives, etc.)
3. Choose the number of words to generate
4. Click "Generate Vocabulary" to create new Latin vocab words
5. Review the generated vocabulary, including:
   - Word forms and grammatical information
   - English definitions
   - Classical Latin example sentences
   - English translations
6. Use the Export button to save to JSON
7. Use the Import tab to load existing vocabulary files
