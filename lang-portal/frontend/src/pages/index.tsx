import { useEffect, useState } from 'react';
import { VocabularyList } from '../components/VocabularyList';
import { api, Word } from '../services/api';

export default function Home() {
  const [words, setWords] = useState<Word[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const [stats, setStats] = useState<{
    success_rate?: number;
    total_study_sessions?: number;
    study_streak_days?: number;
  }>({});

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [wordsResponse, statsResponse] = await Promise.all([
          api.getWords(),
          api.getQuickStats()
        ]);
        setWords(wordsResponse.items);
        setStats(statsResponse);
      } catch (err) {
        setError('Cannot connect to backend server. Please make sure the Go backend is running on port 8080.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-6xl w-full mx-auto px-8 py-6">
        <h1 className="text-4xl font-bold mb-8 text-center text-gray-800">
          French Vocabulary Builder
        </h1>
        
        {/* Stats Section - fixed height */}
        {!loading && !error && (
          <div className="grid grid-cols-3 gap-8 mb-8">
            <div className="bg-white p-6 rounded-lg shadow-lg text-center">
              <div className="text-3xl font-bold text-blue-600">
                {stats.success_rate?.toFixed(1)}%
              </div>
              <div className="text-lg text-gray-600 mt-2">Success Rate</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-lg text-center">
              <div className="text-3xl font-bold text-blue-600">
                {stats.total_study_sessions || 0}
              </div>
              <div className="text-lg text-gray-600 mt-2">Study Sessions</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-lg text-center">
              <div className="text-3xl font-bold text-blue-600">
                {stats.study_streak_days || 0}
              </div>
              <div className="text-lg text-gray-600 mt-2">Day Streak</div>
            </div>
          </div>
        )}
        
        {/* Main content area - no scrolling */}
        <div className="bg-gray-100 w-full">
          <VocabularyList 
            items={words} 
            loading={loading}
            error={error}
          />
        </div>
      </div>
    </div>
  );
}
