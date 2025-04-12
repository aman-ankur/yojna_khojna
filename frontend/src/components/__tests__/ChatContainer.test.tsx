import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import ChatContainer from '../ChatContainer';
import { chatService } from '../../services/api';

// Mock the sub-components to focus on container functionality
vi.mock('../WelcomeHeader', () => ({
  default: ({ userName }: { userName?: string }) => (
    <div data-testid="welcome-header">Welcome Header: {userName}</div>
  )
}));

vi.mock('../SuggestedPrompts', () => ({
  default: ({ onPromptClick }: { onPromptClick?: (text: string) => void }) => (
    <div data-testid="suggested-prompts">
      <button onClick={() => onPromptClick?.('Test prompt')} data-testid="sample-prompt">
        Test Prompt
      </button>
    </div>
  )
}));

vi.mock('../ChatMessages', () => ({
  default: ({ messages, isLoading }: { messages: any[], isLoading?: boolean }) => (
    <div data-testid="chat-messages">
      <div data-testid="message-count">{messages.length}</div>
      <div data-testid="is-loading">{isLoading ? 'true' : 'false'}</div>
      {messages.map((msg, i) => (
        <div key={i} data-testid={`message-${msg.role}`}>
          {msg.content}
        </div>
      ))}
    </div>
  )
}));

vi.mock('../ChatInput', () => ({
  default: ({ 
    onSendMessage,
    disabled,
    isConversationStarted 
  }: { 
    onSendMessage?: (text: string) => void,
    disabled?: boolean,
    isConversationStarted?: boolean
  }) => (
    <div data-testid="chat-input">
      <div data-testid="is-disabled">{disabled ? 'true' : 'false'}</div>
      <div data-testid="conversation-started">{isConversationStarted ? 'true' : 'false'}</div>
      <button 
        onClick={() => onSendMessage?.('Test message')} 
        data-testid="send-button"
      >
        Send
      </button>
    </div>
  )
}));

// Mock the language context
vi.mock('../LanguageToggle', () => ({
  useLanguage: () => ({
    t: {
      error: 'An error occurred'
    }
  })
}));

// Mock the chatService
vi.mock('../../services/api', () => ({
  chatService: {
    sendMessage: vi.fn()
  }
}));

describe('ChatContainer', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    // Default mock implementation
    vi.mocked(chatService.sendMessage).mockResolvedValue({
      answer: 'Mock response',
      updated_history: [
        { role: 'user', content: 'Test message' },
        { role: 'assistant', content: 'Mock response' }
      ]
    });
  });

  it('renders the welcome view by default', () => {
    render(<ChatContainer userName="John" />);
    
    // Check that welcome components are rendered
    expect(screen.getByTestId('welcome-header')).toBeInTheDocument();
    expect(screen.getByTestId('suggested-prompts')).toBeInTheDocument();
    
    // Chat messages should not be visible yet
    expect(screen.queryByTestId('chat-messages')).not.toBeInTheDocument();
    
    // Chat input should be rendered with conversation not started
    expect(screen.getByTestId('chat-input')).toBeInTheDocument();
    expect(screen.getByTestId('conversation-started')).toHaveTextContent('false');
  });
  
  it('transitions to chat view when a message is sent', async () => {
    render(<ChatContainer userName="John" />);
    
    // Send a message
    fireEvent.click(screen.getByTestId('send-button'));
    
    // Wait for state to update
    await waitFor(() => {
      // Welcome view components should be removed
      expect(screen.queryByTestId('welcome-header')).not.toBeInTheDocument();
      expect(screen.queryByTestId('suggested-prompts')).not.toBeInTheDocument();
      
      // Chat messages should now be visible
      expect(screen.getByTestId('chat-messages')).toBeInTheDocument();
      
      // Chat input should show conversation started
      expect(screen.getByTestId('conversation-started')).toHaveTextContent('true');
    });
  });
  
  it('transitions to chat view when a prompt is clicked', async () => {
    render(<ChatContainer userName="John" />);
    
    // Click a suggested prompt
    fireEvent.click(screen.getByTestId('sample-prompt'));
    
    // Wait for state to update
    await waitFor(() => {
      // Welcome view should be gone
      expect(screen.queryByTestId('welcome-header')).not.toBeInTheDocument();
      
      // Chat view should be visible
      expect(screen.getByTestId('chat-messages')).toBeInTheDocument();
    });
  });
  
  it('sends message to API and updates messages state', async () => {
    render(<ChatContainer userName="John" />);
    
    // Send a message
    fireEvent.click(screen.getByTestId('send-button'));
    
    // Check that the API was called
    await waitFor(() => {
      expect(chatService.sendMessage).toHaveBeenCalledWith({
        question: 'Test message',
        chat_history: [] // Initial history is empty
      });
    });
    
    // Wait for messages to be updated
    await waitFor(() => {
      // Should display two messages (user and assistant)
      expect(screen.getByTestId('message-count')).toHaveTextContent('2');
      expect(screen.getByTestId('message-user')).toHaveTextContent('Test message');
      expect(screen.getByTestId('message-assistant')).toHaveTextContent('Mock response');
    });
  });
  
  it('shows loading state while waiting for API response', async () => {
    // Make the API take a moment to respond
    vi.mocked(chatService.sendMessage).mockImplementation(() => {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
            answer: 'Delayed response',
            updated_history: [
              { role: 'user', content: 'Test message' },
              { role: 'assistant', content: 'Delayed response' }
            ]
          });
        }, 100);
      });
    });
    
    render(<ChatContainer userName="John" />);
    
    // Send a message
    fireEvent.click(screen.getByTestId('send-button'));
    
    // Input should be disabled while loading
    await waitFor(() => {
      expect(screen.getByTestId('is-disabled')).toHaveTextContent('true');
      expect(screen.getByTestId('is-loading')).toHaveTextContent('true');
    });
    
    // Wait for loading to finish
    await waitFor(() => {
      expect(screen.getByTestId('is-disabled')).toHaveTextContent('false');
      expect(screen.getByTestId('is-loading')).toHaveTextContent('false');
    }, { timeout: 200 });
  });
  
  it('shows error message when API call fails', async () => {
    // Mock API to throw an error
    vi.mocked(chatService.sendMessage).mockRejectedValue(new Error('API error'));
    
    render(<ChatContainer userName="John" />);
    
    // Send a message
    fireEvent.click(screen.getByTestId('send-button'));
    
    // Wait for error to be displayed
    await waitFor(() => {
      // Should show error alert
      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(screen.getByRole('alert')).toHaveTextContent('An error occurred');
    });
  });
}); 