import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ChatMessages from '../components/ChatMessages';
import { Message } from '../services/api';
import { SuggestedQuestion } from '../components/SuggestedQuestions';
import * as suggestionsHook from '../hooks/useSuggestions';

// Mock the useSuggestions hook
jest.mock('../hooks/useSuggestions', () => ({
  useSuggestions: jest.fn()
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

  const mockSendMessage = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    // Setup the mock to return our mock suggestions
    (suggestionsHook.useSuggestions as jest.Mock).mockReturnValue({
      suggestions: mockSuggestions,
      isLoading: false,
      error: null,
      refreshSuggestions: jest.fn()
    });
  });

  test('renders user and assistant messages correctly', () => {
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

  test('renders suggested questions after the last assistant message', () => {
    render(
      <ChatMessages 
        messages={mockMessages} 
        onSendMessage={mockSendMessage}
      />
    );

    // Check for the suggested questions
    mockSuggestions.forEach(suggestion => {
      expect(screen.getByText(suggestion.text)).toBeInTheDocument();
    });
  });

  test('clicking a suggested question calls onSendMessage', () => {
    render(
      <ChatMessages 
        messages={mockMessages} 
        onSendMessage={mockSendMessage}
      />
    );

    // Find and click a suggestion
    const suggestionChip = screen.getByText(mockSuggestions[0].text);
    fireEvent.click(suggestionChip);

    // The mock function should have been called with the question text
    expect(mockSendMessage).toHaveBeenCalledWith(mockSuggestions[0].text);
  });

  test('handles null onSendMessage prop gracefully', () => {
    // Mock console.error to prevent test output pollution
    const originalError = console.error;
    console.error = jest.fn();

    render(
      <ChatMessages 
        messages={mockMessages} 
        // @ts-ignore - deliberately passing null to test error handling
        onSendMessage={null}
      />
    );

    // Find and click a suggestion
    const suggestionChip = screen.getByText(mockSuggestions[0].text);
    fireEvent.click(suggestionChip);

    // Should log the error
    expect(console.error).toHaveBeenCalledWith('onSendMessage is not a function');

    // Restore console.error
    console.error = originalError;
  });

  test('shows loading state for suggestions when loading', () => {
    // Mock the hook to return loading state
    (suggestionsHook.useSuggestions as jest.Mock).mockReturnValue({
      suggestions: [],
      isLoading: true,
      error: null,
      refreshSuggestions: jest.fn()
    });

    render(
      <ChatMessages 
        messages={mockMessages} 
        onSendMessage={mockSendMessage}
      />
    );

    // Should show loading indicator
    expect(screen.getByText('Generating suggestions...')).toBeInTheDocument();
  });

  test('does not show suggestions for user messages', () => {
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

    // The suggestions should not be rendered (they only appear after assistant messages)
    mockSuggestions.forEach(suggestion => {
      expect(screen.queryByText(suggestion.text)).not.toBeInTheDocument();
    });
  });
}); 