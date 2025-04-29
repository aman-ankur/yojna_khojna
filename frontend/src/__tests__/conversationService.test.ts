import { vi, describe, beforeEach, afterEach, it, expect } from 'vitest';
import conversationService from '../services/conversationService';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => {
      return store[key] || null;
    }),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      store = {};
    }),
  };
})();

// Replace the global localStorage with our mock
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
  writable: true,
});

describe('Conversation Service', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorageMock.clear();
    
    // Reset mocks
    vi.clearAllMocks();
  });
  
  afterEach(() => {
    // Clean up after each test
    vi.restoreAllMocks();
  });
  
  it('should initialize user identity if none exists', () => {
    const identity = conversationService.initialize();
    
    // Should have created a browserID
    expect(identity.browserId).toBeDefined();
    expect(identity.createdAt).toBeDefined();
    
    // Should have called localStorage.setItem
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'yk_user_identity',
      expect.any(String)
    );
  });
  
  it('should return existing user identity if it exists', () => {
    // Create a mock identity
    const mockIdentity = {
      browserId: 'test-browser-id',
      createdAt: new Date().toISOString(),
    };
    
    // Store it directly in the mock store to avoid calling setItem
    localStorageMock.getItem.mockReturnValueOnce(JSON.stringify(mockIdentity));
    
    // Initialize and check it returns the existing identity
    const identity = conversationService.initialize();
    expect(identity.browserId).toBe(mockIdentity.browserId);
    
    // Should have called localStorage.getItem but not setItem
    expect(localStorageMock.getItem).toHaveBeenCalledWith('yk_user_identity');
    expect(localStorageMock.setItem).not.toHaveBeenCalled();
  });
  
  it('should create a new conversation', () => {
    const conversation = conversationService.create();
    
    // Verify conversation properties
    expect(conversation).toEqual({
      id: expect.any(String),
      title: 'New Conversation',
      messages: [],
      createdAt: expect.any(String),
      updatedAt: expect.any(String),
    });
    
    // Should have stored the conversation
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'yk_conversations',
      expect.any(String)
    );
    
    // Should have set the current conversation
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'yk_current_conversation',
      conversation.id
    );
  });
  
  it('should throw an error when max conversations limit is reached', () => {
    // Create mock data with MAX_CONVERSATIONS conversations
    const mockConversations = Array(25).fill(null).map((_, i) => ({
      id: `conversation-${i}`,
      title: `Conversation ${i}`,
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }));
    
    // Store in localStorage
    localStorageMock.setItem('yk_conversations', JSON.stringify(mockConversations));
    
    // Attempt to create a new conversation should throw
    expect(() => conversationService.create()).toThrow('Maximum limit of 25 conversations reached');
  });
  
  it('should get all conversations sorted by updateAt', () => {
    // Create mock data with conversations at different times
    const mockConversations = [
      {
        id: 'conversation-1',
        title: 'Conversation 1',
        messages: [],
        createdAt: new Date('2023-01-01').toISOString(),
        updatedAt: new Date('2023-01-01').toISOString(),
      },
      {
        id: 'conversation-2',
        title: 'Conversation 2',
        messages: [],
        createdAt: new Date('2023-01-02').toISOString(),
        updatedAt: new Date('2023-01-05').toISOString(), // Most recent
      },
      {
        id: 'conversation-3',
        title: 'Conversation 3',
        messages: [],
        createdAt: new Date('2023-01-03').toISOString(),
        updatedAt: new Date('2023-01-03').toISOString(),
      },
    ];
    
    // Store in localStorage
    localStorageMock.setItem('yk_conversations', JSON.stringify(mockConversations));
    
    // Get all conversations
    const conversations = conversationService.getAll();
    
    // Should be sorted by updatedAt (most recent first)
    expect(conversations[0].id).toBe('conversation-2');
    expect(conversations[1].id).toBe('conversation-3');
    expect(conversations[2].id).toBe('conversation-1');
  });
  
  it('should add messages to a conversation', () => {
    // Create a conversation
    const conversation = conversationService.create();
    
    // Add a message
    const updatedConversation = conversationService.addMessage(conversation.id, {
      role: 'user',
      content: 'Test message',
    });
    
    // Should have updated the conversation with the message
    expect(updatedConversation.messages).toHaveLength(1);
    expect(updatedConversation.messages[0]).toEqual({
      id: expect.any(String),
      role: 'user',
      content: 'Test message',
      timestamp: expect.any(String),
    });
    
    // Add another message
    const finalConversation = conversationService.addMessage(conversation.id, {
      role: 'assistant',
      content: 'Test response',
    });
    
    // Should have updated the conversation with both messages
    expect(finalConversation.messages).toHaveLength(2);
    expect(finalConversation.messages[1]).toEqual({
      id: expect.any(String),
      role: 'assistant',
      content: 'Test response',
      timestamp: expect.any(String),
    });
  });
  
  it('should generate a title after adding enough messages', () => {
    // Create a conversation
    const conversation = conversationService.create();
    expect(conversation.title).toBe('New Conversation');
    
    // Add a user message
    const updatedConversation = conversationService.addMessage(conversation.id, {
      role: 'user',
      content: 'What is the eligibility for PM Kisan Yojana?',
    });
    
    // Add assistant response
    const finalConversation = conversationService.addMessage(updatedConversation.id, {
      role: 'assistant',
      content: 'The eligibility criteria includes...',
    });
    
    // Title should be generated from first user message
    expect(finalConversation.title).toBe('What is the eligibility for PM Ki...');
  });
  
  it('should delete a conversation', () => {
    // Create a conversation
    const conversation = conversationService.create();
    
    // Delete it
    conversationService.delete(conversation.id);
    
    // Should not exist anymore
    const conversations = conversationService.getAll();
    expect(conversations).toHaveLength(0);
    
    // Current conversation should be cleared
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('yk_current_conversation');
  });
}); 