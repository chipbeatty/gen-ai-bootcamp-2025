import React from 'react';
import { Word } from '../services/api';

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
      {items.map((item, index) => (
        <div 
          key={index}
          className="p-5 mb-4 bg-white rounded-lg shadow"
        >
          <div className="space-y-1">
            <div className="text-lg font-semibold">
              Word: {item.french_word}
              {item.pronunciation_url && (
                <button 
                  className="ml-2 text-blue-500 hover:text-blue-700"
                  onClick={() => new Audio(item.pronunciation_url).play()}
                >
                  🔊
                </button>
              )}
            </div>
            <div className="text-gray-700">
              Translation: {item.english_translation}
            </div>
            {item.context && (
              <div className="text-gray-600 italic">
                Context: {item.context}
              </div>
            )}
            {(item.correct_count !== undefined || item.wrong_count !== undefined) && (
              <div className="text-sm text-gray-500 mt-2">
                Progress: {item.correct_count || 0} correct, {item.wrong_count || 0} incorrect
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};
