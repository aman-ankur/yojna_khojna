import { render, screen, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';
import LanguageToggle, { LanguageProvider, useLanguage } from '../LanguageToggle';

// Create a test component that uses the language context
const TestComponent = () => {
  const { language, t } = useLanguage();
  return (
    <div>
      <div data-testid="current-language">{language}</div>
      <div data-testid="welcome-text">{t.welcome}</div>
      <div data-testid="question-text">{t.question}</div>
    </div>
  );
};

describe('LanguageToggle', () => {
  it('renders the toggle button with correct text based on language', () => {
    render(
      <LanguageProvider>
        <LanguageToggle />
      </LanguageProvider>
    );
    
    // Hindi is default, so button should show "EN"
    expect(screen.getByText('EN')).toBeInTheDocument();
  });
  
  it('changes language when clicked', () => {
    render(
      <LanguageProvider>
        <LanguageToggle />
        <TestComponent />
      </LanguageProvider>
    );
    
    // Default language should be Hindi
    expect(screen.getByTestId('current-language')).toHaveTextContent('hi');
    
    // Click the toggle button
    fireEvent.click(screen.getByText('EN'));
    
    // Language should change to English and button should show "हि"
    expect(screen.getByTestId('current-language')).toHaveTextContent('en');
    expect(screen.getByText('हि')).toBeInTheDocument();
  });
});

describe('LanguageProvider', () => {
  it('provides correct translations for Hindi (default)', () => {
    render(
      <LanguageProvider>
        <TestComponent />
      </LanguageProvider>
    );
    
    // Check Hindi translations
    expect(screen.getByTestId('welcome-text')).toHaveTextContent('नमस्ते');
    expect(screen.getByTestId('question-text')).toHaveTextContent('आप क्या जानना चाहेंगे?');
  });
  
  it('changes translations when language is switched', () => {
    render(
      <LanguageProvider>
        <LanguageToggle />
        <TestComponent />
      </LanguageProvider>
    );
    
    // Switch to English
    fireEvent.click(screen.getByText('EN'));
    
    // Check English translations
    expect(screen.getByTestId('welcome-text')).toHaveTextContent('Hello');
    expect(screen.getByTestId('question-text')).toHaveTextContent('What would you like to know?');
  });
}); 