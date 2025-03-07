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
    <main className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8 text-center">
          French Vocabulary Builder
        </h1>
        
        {/* Stats Section */}
        {!loading && !error && (
          <div className="grid grid-cols-3 gap-4 mb-8">
            <div className="bg-white p-4 rounded-lg shadow text-center">
              <div className="text-2xl font-bold text-blue-600">
                {stats.success_rate?.toFixed(1)}%
              </div>
              <div className="text-gray-600">Success Rate</div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow text-center">
              <div className="text-2xl font-bold text-green-600">
                {stats.total_study_sessions}
              </div>
              <div className="text-gray-600">Study Sessions</div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow text-center">
              <div className="text-2xl font-bold text-purple-600">
                {stats.study_streak_days}
              </div>
              <div className="text-gray-600">Day Streak</div>
            </div>
          </div>
        )}
        
        {/* No scrolling in content sections - full height display */}
        <div className="min-h-[calc(100vh-12rem)]">
          <VocabularyList 
            items={words} 
            loading={loading}
            error={error}
          />
        </div>
      </div>
    </main>
  );
}
