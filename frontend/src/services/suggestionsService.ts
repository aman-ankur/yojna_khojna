import api from './api';
import { SuggestedQuestion } from '../components/SuggestedQuestions';
import { Message } from './api';

export interface SuggestionsRequest {
  conversationId?: string;
  lastResponseId?: string;
  question: string;
  answer: string;
  chat_history: Message[];
}

export interface SuggestionsResponse {
  suggestions: SuggestedQuestion[];
}

/**
 * Service for fetching suggested follow-up questions
 */
export const suggestionsService = {
  /**
   * Get suggested follow-up questions based on conversation context
   */
  getSuggestions: async (request: SuggestionsRequest): Promise<SuggestedQuestion[]> => {
    try {
      const response = await api.post<SuggestionsResponse>('/suggested-questions', request);
      return response.data.suggestions;
    } catch (error) {
      console.error('Error fetching suggestions:', error);
      return []; // Return empty array on error to gracefully handle failures
    }
  }
};

export default suggestionsService; 