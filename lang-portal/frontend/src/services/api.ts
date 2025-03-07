import axios from 'axios';

const API_BASE_URL = 'http://localhost:8080/api';

export interface Word {
  french_word: string;
  english_translation: string;
  context?: string;
  correct_count?: number;
  wrong_count?: number;
  pronunciation_url?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: {
    current_page: number;
    total_pages: number;
    total_items: number;
    items_per_page: number;
  };
}

export const api = {
  // Get paginated list of words
  getWords: async (page = 1): Promise<PaginatedResponse<Word>> => {
    const response = await axios.get(`${API_BASE_URL}/words?page=${page}`);
    return response.data;
  },

  // Get quick stats
  getQuickStats: async () => {
    const response = await axios.get(`${API_BASE_URL}/dashboard/quick-stats`);
    return response.data;
  },

  // Get study progress
  getStudyProgress: async () => {
    const response = await axios.get(`${API_BASE_URL}/dashboard/study_progress`);
    return response.data;
  }
};
