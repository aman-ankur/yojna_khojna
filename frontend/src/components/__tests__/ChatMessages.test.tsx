import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';
import ChatMessages, { AssistantMessage, UserMessage, TypingIndicator } from '../ChatMessages';

describe('ChatMessages', () => {
  it('renders an empty state message when no messages are provided', () => {
    render(<ChatMessages messages={[]} />);
    expect(screen.getByText('Start a conversation to see messages here.')).toBeInTheDocument();
  });
  
  it('renders user and assistant messages correctly', () => {
    const messages = [
      { role: 'user', content: 'Hello, how can I apply for PMAY?' },
      { role: 'assistant', content: 'To apply for PMAY, you need to follow these steps...' }
    ];
    
    render(<ChatMessages messages={messages} />);
    
    // Check that both message contents are rendered
    expect(screen.getByText('Hello, how can I apply for PMAY?')).toBeInTheDocument();
    expect(screen.getByText('To apply for PMAY, you need to follow these steps...')).toBeInTheDocument();
  });
  
  it('shows the typing indicator when isLoading is true', () => {
    render(<ChatMessages messages={[]} isLoading={true} />);
    
    // Look for the avatar in the typing indicator
    const avatars = screen.getAllByText('Y');
    expect(avatars.length).toBeGreaterThanOrEqual(1);
    
    // The empty state message should not be shown when loading
    expect(screen.queryByText('Start a conversation to see messages here.')).not.toBeInTheDocument();
  });
});

describe('Message Components', () => {
  it('renders UserMessage correctly', () => {
    render(<UserMessage content="This is a user message" />);
    
    // Check that the message content is rendered
    expect(screen.getByText('This is a user message')).toBeInTheDocument();
    
    // Check that the user avatar is rendered
    expect(screen.getByText('U')).toBeInTheDocument();
  });
  
  it('renders AssistantMessage correctly', () => {
    render(<AssistantMessage content="This is an assistant message" />);
    
    // Check that the message content is rendered
    expect(screen.getByText('This is an assistant message')).toBeInTheDocument();
    
    // Check that the assistant avatar is rendered
    expect(screen.getByText('Y')).toBeInTheDocument();
  });
  
  it('renders AssistantMessage with ReactNode content', () => {
    const content = <div data-testid="custom-content">Custom content</div>;
    render(<AssistantMessage content={content} />);
    
    // Check that the custom content is rendered
    expect(screen.getByTestId('custom-content')).toBeInTheDocument();
  });
  
  it('renders TypingIndicator correctly', () => {
    render(<TypingIndicator />);
    
    // Check that the assistant avatar is rendered
    expect(screen.getByText('Y')).toBeInTheDocument();
  });
}); 