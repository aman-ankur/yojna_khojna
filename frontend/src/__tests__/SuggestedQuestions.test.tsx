import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import SuggestedQuestions, { SuggestedQuestion } from '../components/SuggestedQuestions';

describe('SuggestedQuestions Component', () => {
  const mockSuggestions: SuggestedQuestion[] = [
    { id: '1', text: 'What documents do I need for this scheme?' },
    { id: '2', text: 'Am I eligible for this scheme?' },
    { id: '3', text: 'How do I apply for this scheme?' },
  ];

  const mockOnQuestionClick = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state correctly', () => {
    render(
      <SuggestedQuestions
        suggestions={[]}
        onQuestionClick={mockOnQuestionClick}
        isLoading={true}
      />
    );

    expect(screen.getByText('Generating suggestions...')).toBeInTheDocument();
  });

  test('renders nothing when no suggestions are provided', () => {
    const { container } = render(
      <SuggestedQuestions
        suggestions={[]}
        onQuestionClick={mockOnQuestionClick}
        isLoading={false}
      />
    );

    expect(container.firstChild).toBeNull();
  });

  test('renders suggestions as chips', () => {
    render(
      <SuggestedQuestions
        suggestions={mockSuggestions}
        onQuestionClick={mockOnQuestionClick}
        isLoading={false}
      />
    );

    mockSuggestions.forEach((suggestion) => {
      expect(screen.getByText(suggestion.text)).toBeInTheDocument();
    });
  });

  test('calls onQuestionClick when a suggestion chip is clicked', () => {
    render(
      <SuggestedQuestions
        suggestions={mockSuggestions}
        onQuestionClick={mockOnQuestionClick}
        isLoading={false}
      />
    );

    const firstSuggestion = screen.getByText(mockSuggestions[0].text);
    fireEvent.click(firstSuggestion);

    expect(mockOnQuestionClick).toHaveBeenCalledWith(mockSuggestions[0].text);
  });

  test('handles null onQuestionClick without crashing', () => {
    // Mock console.error to capture the error message
    const originalError = console.error;
    console.error = jest.fn();

    render(
      <SuggestedQuestions
        suggestions={mockSuggestions}
        // @ts-ignore - deliberately passing null to test error handling
        onQuestionClick={null}
        isLoading={false}
      />
    );

    const firstSuggestion = screen.getByText(mockSuggestions[0].text);
    
    // This shouldn't throw an error when clicked
    fireEvent.click(firstSuggestion);
    
    // Should log the error
    expect(console.error).toHaveBeenCalledWith('Question click handler is not a function');
    
    // Restore console.error
    console.error = originalError;
  });

  test('renders long question text with ellipsis', () => {
    const longQuestion = { 
      id: 'long', 
      text: 'This is a very long question that should be truncated with ellipsis when displayed in the SuggestedQuestions component'
    };
    
    render(
      <SuggestedQuestions
        suggestions={[longQuestion]}
        onQuestionClick={mockOnQuestionClick}
        isLoading={false}
      />
    );
    
    const chipElement = screen.getByText(longQuestion.text);
    const parentElement = chipElement.closest('div');
    
    expect(chipElement).toBeInTheDocument();
    // Check that text is truncated in UI (this is a simplistic check since we can't easily check CSS)
    expect(parentElement).toHaveStyle('overflow: hidden');
    expect(parentElement).toHaveStyle('text-overflow: ellipsis');
  });
}); 