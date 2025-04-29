import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useSuggestions } from '../hooks/useSuggestions';
import { suggestionsService } from '../services/suggestionsService';
import { Message } from '../services/api';

// Mock the suggestionsService
vi.mock('../services/suggestionsService', () => ({
  suggestionsService: {
    getSuggestions: vi.fn(),
  },
}));

describe('useSuggestions Hook', () => {
  const mockSuggestions = [
    { id: '1', text: 'What documents do I need?' },
    { id: '2', text: 'Am I eligible for this scheme?' },
  ];

  const mockQuestion = 'What is Pradhan Mantri Awas Yojana?';
  const mockAnswer = 'It is a housing scheme.';
  const mockChatHistory: Message[] = [
    { role: 'user', content: mockQuestion },
    { role: 'assistant', content: mockAnswer },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch suggestions when provided with valid inputs', async () => {
    // Setup mock response
    vi.mocked(suggestionsService.getSuggestions).mockResolvedValueOnce(mockSuggestions);

    // Render the hook
    const { result } = renderHook(() =>
      useSuggestions(mockQuestion, mockAnswer, mockChatHistory)
    );

    // Initially, it should be loading with empty suggestions
    expect(result.current.isLoading).toBe(true);
    expect(result.current.suggestions).toEqual([]);

    // Wait for the async operation to complete
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // After loading, it should have suggestions and not be loading
    expect(result.current.suggestions).toEqual(mockSuggestions);
    expect(result.current.error).toBeNull();

    // Verify the service was called with the right parameters
    expect(suggestionsService.getSuggestions).toHaveBeenCalledWith({
      question: mockQuestion,
      answer: mockAnswer,
      chat_history: mockChatHistory,
    });
  });

  it('should not fetch suggestions when inputs are empty', () => {
    // Render the hook with empty inputs
    const { result } = renderHook(() => useSuggestions('', '', []));

    // Should not be loading and have empty suggestions
    expect(result.current.isLoading).toBe(false);
    expect(result.current.suggestions).toEqual([]);

    // Service should not have been called
    expect(suggestionsService.getSuggestions).not.toHaveBeenCalled();
  });

  it('should handle errors gracefully', async () => {
    // Setup mock to throw an error
    const mockError = new Error('Failed to fetch suggestions');
    vi.mocked(suggestionsService.getSuggestions).mockRejectedValueOnce(mockError);

    // Render the hook
    const { result } = renderHook(() =>
      useSuggestions(mockQuestion, mockAnswer, mockChatHistory)
    );

    // Wait for the async operation to complete
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // After error, it should not be loading and have empty suggestions
    expect(result.current.suggestions).toEqual([]);
    expect(result.current.error).toEqual(mockError);
  });

  it('should refresh suggestions when calling refreshSuggestions', async () => {
    // Setup mock responses
    vi.mocked(suggestionsService.getSuggestions)
      .mockResolvedValueOnce(mockSuggestions)
      .mockResolvedValueOnce([...mockSuggestions, { id: '3', text: 'New suggestion' }]);

    // Render the hook
    const { result } = renderHook(() =>
      useSuggestions(mockQuestion, mockAnswer, mockChatHistory)
    );

    // Wait for first fetch to complete
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Initial state after first fetch
    expect(result.current.suggestions).toEqual(mockSuggestions);

    // Call refresh function
    await result.current.refreshSuggestions();

    // Wait for second fetch to complete
    await waitFor(() => {
      expect(result.current.suggestions).toHaveLength(3);
    });

    // Service should have been called twice
    expect(suggestionsService.getSuggestions).toHaveBeenCalledTimes(2);
  });
}); 