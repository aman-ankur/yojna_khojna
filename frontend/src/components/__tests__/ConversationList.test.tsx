import { render, screen, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';
import ConversationList from '../ConversationList';
import { Conversation } from '../../services/conversationService';

// Mock LanguageToggle
vi.mock('../LanguageToggle', () => ({
  useLanguage: () => ({
    t: {
      conversations: 'Conversations',
      newConversation: 'New Conversation',
      noConversations: 'No conversations yet',
      pinnedConversations: 'Pinned',
      otherConversations: 'Other Conversations'
    }
  })
}));

// Mock data
const mockConversations: Conversation[] = [
  {
    id: 'conv1',
    title: 'Conversation 1',
    messages: [],
    createdAt: '2023-01-01T00:00:00.000Z',
    updatedAt: '2023-01-01T01:00:00.000Z',
    isPinned: false
  },
  {
    id: 'conv2',
    title: 'Conversation 2',
    messages: [],
    createdAt: '2023-01-02T00:00:00.000Z',
    updatedAt: '2023-01-02T01:00:00.000Z',
    isPinned: false
  }
];

const mockPinnedConversations: Conversation[] = [
  {
    id: 'pinned1',
    title: 'Pinned Conversation 1',
    messages: [],
    createdAt: '2023-01-03T00:00:00.000Z',
    updatedAt: '2023-01-03T01:00:00.000Z',
    isPinned: true,
    pinnedAt: '2023-01-03T01:30:00.000Z'
  },
  {
    id: 'pinned2',
    title: 'Pinned Conversation 2',
    messages: [],
    createdAt: '2023-01-04T00:00:00.000Z',
    updatedAt: '2023-01-04T01:00:00.000Z',
    isPinned: true,
    pinnedAt: '2023-01-04T01:30:00.000Z'
  }
];

// Mock functions
const mockOnSelectConversation = vi.fn();
const mockOnDeleteConversation = vi.fn();
const mockOnRenameConversation = vi.fn();
const mockOnPinConversation = vi.fn();
const mockOnUnpinConversation = vi.fn();
const mockOnNewConversation = vi.fn();

describe('ConversationList', () => {
  it('renders new conversation button', () => {
    render(
      <ConversationList
        conversations={[]}
        currentConversationId={null}
        loading={false}
        onSelectConversation={mockOnSelectConversation}
        onDeleteConversation={mockOnDeleteConversation}
        onNewConversation={mockOnNewConversation}
      />
    );
    
    expect(screen.getByText('New Conversation')).toBeInTheDocument();
  });
  
  it('shows loading spinner when loading', () => {
    render(
      <ConversationList
        conversations={[]}
        currentConversationId={null}
        loading={true}
        onSelectConversation={mockOnSelectConversation}
        onDeleteConversation={mockOnDeleteConversation}
        onNewConversation={mockOnNewConversation}
      />
    );
    
    // MUI's CircularProgress doesn't have a testId by default, so check for role
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });
  
  it('shows "No conversations" when no conversations', () => {
    render(
      <ConversationList
        conversations={[]}
        currentConversationId={null}
        loading={false}
        onSelectConversation={mockOnSelectConversation}
        onDeleteConversation={mockOnDeleteConversation}
        onNewConversation={mockOnNewConversation}
      />
    );
    
    expect(screen.getByText('No conversations yet')).toBeInTheDocument();
  });
  
  it('renders a list of conversations', () => {
    render(
      <ConversationList
        conversations={mockConversations}
        currentConversationId={null}
        loading={false}
        onSelectConversation={mockOnSelectConversation}
        onDeleteConversation={mockOnDeleteConversation}
        onNewConversation={mockOnNewConversation}
      />
    );
    
    expect(screen.getByText('Conversation 1')).toBeInTheDocument();
    expect(screen.getByText('Conversation 2')).toBeInTheDocument();
  });
  
  it('renders pinned conversations separately from unpinned ones', () => {
    render(
      <ConversationList
        conversations={[...mockPinnedConversations, ...mockConversations]}
        pinnedConversations={mockPinnedConversations}
        unpinnedConversations={mockConversations}
        currentConversationId={null}
        loading={false}
        onSelectConversation={mockOnSelectConversation}
        onDeleteConversation={mockOnDeleteConversation}
        onPinConversation={mockOnPinConversation}
        onUnpinConversation={mockOnUnpinConversation}
        onNewConversation={mockOnNewConversation}
      />
    );
    
    // Check for section headings
    expect(screen.getByText('Pinned')).toBeInTheDocument();
    expect(screen.getByText('Other Conversations')).toBeInTheDocument();
    
    // Check for pinned conversations
    expect(screen.getByText('Pinned Conversation 1')).toBeInTheDocument();
    expect(screen.getByText('Pinned Conversation 2')).toBeInTheDocument();
    
    // Check for unpinned conversations
    expect(screen.getByText('Conversation 1')).toBeInTheDocument();
    expect(screen.getByText('Conversation 2')).toBeInTheDocument();
  });
  
  it('calls the new conversation callback when button is clicked', () => {
    render(
      <ConversationList
        conversations={[]}
        currentConversationId={null}
        loading={false}
        onSelectConversation={mockOnSelectConversation}
        onDeleteConversation={mockOnDeleteConversation}
        onNewConversation={mockOnNewConversation}
      />
    );
    
    const newButton = screen.getByRole('button', { name: 'New Conversation' });
    fireEvent.click(newButton);
    
    expect(mockOnNewConversation).toHaveBeenCalledTimes(1);
  });
}); 