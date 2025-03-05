document.getElementById('searchForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const songInput = document.getElementById('songInput').value.trim();
    if (!songInput) return;

    // Show loading, hide other sections
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');
    document.getElementById('error').classList.add('hidden');

    try {
        const response = await fetch('/api/agent', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message_request: songInput
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to fetch lyrics');
        }

        const data = await response.json();
        
        // Clean and format lyrics
        const cleanLyrics = data.lyrics
            .split('\n')
            .filter(line => line.trim())
            .join('\n');
        
        // Display lyrics
        const lyricsContent = document.getElementById('lyricsContent');
        lyricsContent.innerHTML = `<pre>${cleanLyrics}</pre>`;

        // Display vocabulary
        const vocabularyContent = document.getElementById('vocabularyContent');
        vocabularyContent.innerHTML = data.vocabulary.map(item => `
            <div class="vocabulary-item">
                <div class="word-line">Word: <span class="vocabulary-word">${item.word}</span></div>
                <div class="translation-line">Translation: <span class="vocabulary-translation">${item.translation}</span></div>
                <div class="context-line">Context: <span class="vocabulary-context">${item.context}</span></div>
            </div>
        `).join('');

        // Show results
        document.getElementById('results').classList.remove('hidden');
    } catch (error) {
        document.getElementById('error').classList.remove('hidden');
        document.getElementById('error').querySelector('p').textContent = 
            `Error: ${error.message}`;
    } finally {
        document.getElementById('loading').classList.add('hidden');
    }
});
