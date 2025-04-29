import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import ChatMessages from '../components/ChatMessages';
import { Message } from '../services/api';
import { SuggestedQuestion } from '../components/SuggestedQuestions';
import * as suggestionsHook from '../hooks/useSuggestions';

// Mock the useSuggestions hook
vi.mock('../hooks/useSuggestions', async () => {
  const actual = await vi.importActual('../hooks/useSuggestions');
  return {
    ...actual,
    useSuggestions: vi.fn()
  };
});

// Mock SuggestedQuestions component to avoid text truncation issues
vi.mock('../components/SuggestedQuestions', () => ({
  default: ({ suggestions, isLoading, onQuestionClick }) => {
    if (isLoading) return <div data-testid="loading-suggestions">Generating suggestions...</div>;
    if (!suggestions || suggestions.length === 0) return null;
    return (
      <div data-testid="suggested-questions">
        {suggestions.map(suggestion => (
          <button 
            key={suggestion.id}
            onClick={() => onQuestionClick?.(suggestion.text)}
            data-testid={`suggestion-${suggestion.id}`}
            aria-label={suggestion.text}
          >
            {suggestion.text}
          </button>
        ))}
      </div>
    );
  }
}));

describe('ChatMessages Component', () => {
  const mockMessages: Message[] = [
    { role: 'user', content: 'What is Pradhan Mantri Awas Yojana?' },
    { role: 'assistant', content: 'It is a housing scheme by the government of India.' }
  ];

  const mockSuggestions: SuggestedQuestion[] = [
    { id: '1', text: 'What documents do I need?' },
    { id: '2', text: 'Am I eligible for this scheme?' },
    { id: '3', text: 'How do I apply for this scheme?' },
    { id: '4', text: 'When is the deadline to apply?' }
  ];

  const mockSendMessage = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    // Setup the mock to return our mock suggestions
    vi.mocked(suggestionsHook.useSuggestions).mockReturnValue({
      suggestions: mockSuggestions,
      isLoading: false,
      error: null,
      refreshSuggestions: vi.fn()
    });
  });

  it('renders user and assistant messages correctly', () => {
    render(
      <ChatMessages 
        messages={mockMessages} 
        onSendMessage={mockSendMessage}
      />
    );

    // Check that both messages are rendered
    expect(screen.getByText(mockMessages[0].content)).toBeInTheDocument();
    expect(screen.getByText(mockMessages[1].content)).toBeInTheDocument();
  });

  it('renders suggested questions after the last assistant message', () => {
    render(
      <ChatMessages 
        messages={mockMessages} 
        onSendMessage={mockSendMessage}
      />
    );

    // Check for the suggested questions container
    expect(screen.getByTestId('suggested-questions')).toBeInTheDocument();
    
    // Check for specific suggestion buttons (using our mocked component)
    mockSuggestions.forEach(suggestion => {
      expect(screen.getByTestId(`suggestion-${suggestion.id}`)).toBeInTheDocument();
    });
  });

  it('clicking a suggested question calls onSendMessage', () => {
    render(
      <ChatMessages 
        messages={mockMessages} 
        onSendMessage={mockSendMessage}
      />
    );

    // Find and click a suggestion using our test-specific button
    const suggestionButton = screen.getByTestId(`suggestion-${mockSuggestions[0].id}`);
    fireEvent.click(suggestionButton);

    // The mock function should have been called with the question text
    expect(mockSendMessage).toHaveBeenCalledWith(mockSuggestions[0].text);
  });

  it('handles null onSendMessage prop gracefully', () => {
    // Mock console.error to prevent test output pollution
    const originalError = console.error;
    console.error = vi.fn();

    render(
      <ChatMessages 
        messages={mockMessages} 
        // @ts-ignore - deliberately passing null to test error handling
        onSendMessage={null}
      />
    );

    // Find and click a suggestion
    const suggestionButton = screen.getByTestId(`suggestion-${mockSuggestions[0].id}`);
    fireEvent.click(suggestionButton);

    // Should log the error
    expect(console.error).toHaveBeenCalledWith('onSendMessage is not a function');

    // Restore console.error
    console.error = originalError;
  });

  it('shows loading state for suggestions when loading', () => {
    // Mock the hook to return loading state
    vi.mocked(suggestionsHook.useSuggestions).mockReturnValue({
      suggestions: [],
      isLoading: true,
      error: null,
      refreshSuggestions: vi.fn()
    });

    render(
      <ChatMessages 
        messages={mockMessages} 
        onSendMessage={mockSendMessage}
      />
    );

    // Should show loading indicator
    expect(screen.getByTestId('loading-suggestions')).toBeInTheDocument();
  });

  it('does not show suggestions for user messages', () => {
    // Setup with only a user message as the last message
    const userLastMessages = [
      { role: 'assistant', content: 'It is a housing scheme.' },
      { role: 'user', content: 'What documents do I need?' }
    ];

    render(
      <ChatMessages 
        messages={userLastMessages} 
        onSendMessage={mockSendMessage}
      />
    );

    // The suggestions container should not be rendered
    expect(screen.queryByTestId('suggested-questions')).not.toBeInTheDocument();
  });
}); 