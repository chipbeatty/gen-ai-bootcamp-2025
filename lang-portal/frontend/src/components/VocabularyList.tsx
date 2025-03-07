import React from 'react';
import { Word } from '../services/api';

const speak = (text: string) => {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'fr-FR';
  utterance.rate = 0.9; // Slightly slower for better pronunciation
  window.speechSynthesis.speak(utterance);
};

interface VocabularyListProps {
  items: Word[];
  loading?: boolean;
  error?: string;
}

export const VocabularyList: React.FC<VocabularyListProps> = ({ items, loading, error }) => {
  if (loading) {
    return <div className="text-center py-4">Loading vocabulary...</div>;
  }

  if (error) {
    return <div className="text-red-600 text-center py-4">{error}</div>;
  }

  if (!items.length) {
    return <div className="text-center py-4">No vocabulary items found.</div>;
  }

  return (
    <div className="max-w-6xl mx-auto">
      {items.map((item) => (
        <div key={item.id} className="vocab-item">
          {/* Three-line format as per UI preferences */}
          <div className="space-y-4">
            {/* Line 1: Word */}
            <div className="flex">
              <span className="w-32 font-semibold">Word:</span>
              <div className="flex-1 flex items-center">
                <span className="text-xl">{item.french_word}</span>
                <button 
                  className="ml-3 text-blue-600 hover:text-blue-800 focus:outline-none"
                  onClick={() => speak(item.french_word)}
                  aria-label="Play pronunciation"
                >
                  🔊
                </button>
              </div>
            </div>

            {/* Line 2: Translation */}
            <div className="flex">
              <span className="w-32 font-semibold">Translation:</span>
              <span className="flex-1">{item.english_translation}</span>
            </div>

            {/* Line 3: Context (in italics) */}
            {item.context && (
              <div className="flex">
                <span className="w-32 font-semibold">Context:</span>
                <span className="flex-1 italic">{item.context}</span>
              </div>
            )}

            {/* Progress info */}
            <div className="text-sm text-gray-500 mt-4 pt-3 border-t flex items-center gap-2">
              <span className="font-medium">Progress:</span>
              <span>{item.correct_count} correct</span>
              <span>•</span>
              <span>{item.wrong_count} incorrect</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
