import { useState, useEffect } from 'react';
import { suggestionsService, SuggestionsRequest } from '../services/suggestionsService';
import { SuggestedQuestion } from '../components/SuggestedQuestions';
import { Message } from '../services/api';

/**
 * Custom hook to fetch and manage suggested questions
 */
export const useSuggestions = (
  lastQuestion: string,
  lastAnswer: string,
  chatHistory: Message[]
): {
  suggestions: SuggestedQuestion[];
  isLoading: boolean;
  error: Error | null;
  refreshSuggestions: () => Promise<void>;
} => {
  const [suggestions, setSuggestions] = useState<SuggestedQuestion[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  // Function to fetch suggestions
  const fetchSuggestions = async () => {
    // Don't fetch suggestions if there's no conversation yet
    if (!lastQuestion || !lastAnswer) {
      setSuggestions([]);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const request: SuggestionsRequest = {
        question: lastQuestion,
        answer: lastAnswer,
        chat_history: chatHistory,
      };

      const newSuggestions = await suggestionsService.getSuggestions(request);
      setSuggestions(newSuggestions);
    } catch (err) {
      console.error('Error in useSuggestions hook:', err);
      setError(err instanceof Error ? err : new Error('Failed to fetch suggestions'));
      setSuggestions([]); // Clear suggestions on error
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch suggestions when lastAnswer changes
  useEffect(() => {
    fetchSuggestions();
  }, [lastAnswer]);

  return {
    suggestions,
    isLoading,
    error,
    refreshSuggestions: fetchSuggestions,
  };
};

export default useSuggestions; 