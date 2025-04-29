import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';
import WelcomeHeader from '../WelcomeHeader';

// Mock the language context
vi.mock('../LanguageToggle', () => ({
  useLanguage: () => ({
    t: {
      welcome: 'Hello',
      question: 'What would you like to know?',
      subtitle: 'Choose one of the suggestions below or ask your own question'
    },
    language: 'en'
  }),
  default: () => <div data-testid="language-toggle" />
}));

describe('WelcomeHeader', () => {
  it('renders the welcome message with the provided user name', () => {
    render(<WelcomeHeader userName="John" />);
    
    // Check for welcome text (including the name)
    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('John')).toBeInTheDocument();
    
    // Check for the question text
    expect(screen.getByText('What would you like to know?')).toBeInTheDocument();
    
    // Check for subtitle text
    expect(screen.getByText('Choose one of the suggestions below or ask your own question')).toBeInTheDocument();
  });
  
  it('renders the language toggle', () => {
    render(<WelcomeHeader userName="John" />);
    expect(screen.getByTestId('language-toggle')).toBeInTheDocument();
  });
  
  it('renders with default name when userName is not provided', () => {
    render(<WelcomeHeader />);
    
    // The default name is "नागरिक", not "there"
    expect(screen.getByText('नागरिक')).toBeInTheDocument();
  });
}); 