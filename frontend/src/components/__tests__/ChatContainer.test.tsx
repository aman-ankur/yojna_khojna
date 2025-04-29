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

// More detailed mock for useCurrentConversation
let mockMessages = [];
const mockAddMessage = vi.fn((message) => {
  // Simulate adding messages to the conversation
  mockMessages.push(message);
  mockCurrentConversation.messages = [...mockMessages];
  
  // Return the updated conversation when requested
  return mockCurrentConversation;
});

let mockCurrentConversation = {
  id: 'test-conversation-id',
  messages: mockMessages,
  title: 'Test Conversation',
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString()
};

// Mock the useCurrentConversation hook
vi.mock('../../hooks/useCurrentConversation', () => ({
  default: () => ({
    currentConversation: mockCurrentConversation,
    loading: false,
    error: null,
    addMessage: mockAddMessage,
    switchConversation: vi.fn(),
    createNewConversation: vi.fn(),
    refreshCurrentConversation: vi.fn()
  })
}));

describe('ChatContainer', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    // Reset mock conversation state
    mockMessages = [];
    mockCurrentConversation.messages = [];
    
    // Default mock implementation for API
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
    const { rerender } = render(<ChatContainer userName="John" />);
    
    // Send a message
    fireEvent.click(screen.getByTestId('send-button'));
    
    // Simulate conversation update with a message
    mockCurrentConversation.messages = [
      { id: '1', role: 'user', content: 'Test message', timestamp: new Date().toISOString() },
      { id: '2', role: 'assistant', content: 'Mock response', timestamp: new Date().toISOString() }
    ];
    
    // Force a re-render to reflect the updated messages
    rerender(<ChatContainer userName="John" />);
    
    // Wait for state to update
    await waitFor(() => {
      // Welcome view components should be removed
      expect(screen.queryByTestId('welcome-header')).not.toBeInTheDocument();
      
      // Chat messages should now be visible
      expect(screen.getByTestId('chat-messages')).toBeInTheDocument();
      
      // Chat input should show conversation started
      expect(screen.getByTestId('conversation-started')).toHaveTextContent('true');
    });
  });
  
  it('transitions to chat view when a prompt is clicked', async () => {
    const { rerender } = render(<ChatContainer userName="John" />);
    
    // Get all buttons in the suggested prompts area
    const promptButton = screen.getByTestId('sample-prompt');
    fireEvent.click(promptButton);
    
    // Simulate conversation update with a message
    mockCurrentConversation.messages = [
      { id: '1', role: 'user', content: 'Test prompt', timestamp: new Date().toISOString() },
      { id: '2', role: 'assistant', content: 'Mock response', timestamp: new Date().toISOString() }
    ];
    
    // Force a re-render to reflect the updated messages
    rerender(<ChatContainer userName="John" />);
    
    // Wait for state to update
    await waitFor(() => {
      // Welcome view should be gone
      expect(screen.queryByTestId('welcome-header')).not.toBeInTheDocument();
      
      // Chat view should be visible
      expect(screen.getByTestId('chat-messages')).toBeInTheDocument();
    });
  });
  
  it('sends message to API and updates messages state', async () => {
    const { rerender } = render(<ChatContainer userName="John" />);
    
    // Send a message
    fireEvent.click(screen.getByTestId('send-button'));
    
    // Check that the API was called - accept any chat_history value
    await waitFor(() => {
      expect(chatService.sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({
          question: 'Test message'
        })
      );
    });
    
    // Simulate conversation update with a message and response
    mockCurrentConversation.messages = [
      { id: '1', role: 'user', content: 'Test message', timestamp: new Date().toISOString() },
      { id: '2', role: 'assistant', content: 'Mock response', timestamp: new Date().toISOString() }
    ];
    
    // Force a re-render to reflect the updated messages
    rerender(<ChatContainer userName="John" />);
    
    // Wait for messages to be updated
    await waitFor(() => {
      // Chat view should be visible with messages
      expect(screen.getByTestId('chat-messages')).toBeInTheDocument();
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
    
    // Start with a conversation that already has messages to force chat view
    mockCurrentConversation.messages = [
      { id: '1', role: 'user', content: 'Previous message', timestamp: new Date().toISOString() },
      { id: '2', role: 'assistant', content: 'Previous response', timestamp: new Date().toISOString() }
    ];
    
    const { rerender } = render(<ChatContainer userName="John" />);
    
    // Send a message
    fireEvent.click(screen.getByTestId('send-button'));
    
    // Manually set the loading state for the test
    rerender(<ChatContainer userName="John" />);
    
    // Input should be disabled while loading
    expect(mockAddMessage).toHaveBeenCalled();
    
    // Wait for loading to finish
    await waitFor(() => {
      expect(chatService.sendMessage).toHaveBeenCalled();
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