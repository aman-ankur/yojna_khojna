import { render, screen, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';
import SuggestedPrompts from '../SuggestedPrompts';

// Mock the language context
vi.mock('../LanguageToggle', () => ({
  useLanguage: () => ({
    t: {
      eligibility: 'Check eligibility for schemes',
      applicationProcess: 'Ask about application process',
      benefits: 'Get information about scheme benefits',
      govtHelp: 'Ask about government assistance',
      refreshSuggestions: 'Refresh suggestions'
    }
  })
}));

describe('SuggestedPrompts', () => {
  it('renders all prompt cards with correct text', () => {
    render(<SuggestedPrompts />);
    
    // Check that all prompt texts are rendered
    expect(screen.getByText('Check eligibility for schemes')).toBeInTheDocument();
    expect(screen.getByText('Ask about application process')).toBeInTheDocument();
    expect(screen.getByText('Get information about scheme benefits')).toBeInTheDocument();
    expect(screen.getByText('Ask about government assistance')).toBeInTheDocument();
    
    // Check that refresh button is rendered
    expect(screen.getByText('Refresh suggestions')).toBeInTheDocument();
  });
  
  it('calls onPromptClick when a prompt card is clicked', () => {
    const mockClickHandler = vi.fn();
    render(<SuggestedPrompts onPromptClick={mockClickHandler} />);
    
    // Click the first prompt card
    fireEvent.click(screen.getByText('Check eligibility for schemes'));
    
    // Verify the click handler was called with the correct text
    expect(mockClickHandler).toHaveBeenCalledTimes(1);
    expect(mockClickHandler).toHaveBeenCalledWith('Check eligibility for schemes');
  });
  
  it('does not throw an error if onPromptClick is not provided', () => {
    render(<SuggestedPrompts />);
    
    // This should not throw an error
    expect(() => {
      fireEvent.click(screen.getByText('Ask about application process'));
    }).not.toThrow();
  });
}); 