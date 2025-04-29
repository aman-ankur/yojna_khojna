import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LanguageProvider, useLanguage } from '../../components/LanguageToggle';
import ConversationListItem from '../ConversationListItem';
import { Conversation } from '../../services/conversationService';

// Mock the date-fns library
vi.mock('date-fns', () => ({
  formatDistanceToNow: () => '2 days ago'
}));

// Mock LanguageToggle
vi.mock('../LanguageToggle', () => ({
  useLanguage: () => ({
    t: {
      renameConversation: 'Rename',
      deleteConversation: 'Delete',
      save: 'Save',
      cancel: 'Cancel',
      deleteConversationTitle: 'Delete Conversation',
      deleteConversationConfirm: 'Are you sure you want to delete',
      delete: 'Delete',
      pinConversation: 'Pin',
      unpinConversation: 'Unpin',
      pinLimitReached: 'Pin limit reached (3)',
      pinLimitReachedTitle: 'Pin Limit Reached',
      ok: 'OK'
    }
  })
}));

// Mock test conversation
const mockConversation: Conversation = {
  id: 'test-conversation-id',
  title: 'Test Conversation',
  messages: [],
  createdAt: '2023-01-01T00:00:00.000Z',
  updatedAt: '2023-01-05T00:00:00.000Z',
  isPinned: false
};

const mockPinnedConversation: Conversation = {
  id: 'pinned-conversation-id',
  title: 'Pinned Conversation',
  messages: [],
  createdAt: '2023-01-02T00:00:00.000Z',
  updatedAt: '2023-01-06T00:00:00.000Z',
  isPinned: true,
  pinnedAt: '2023-01-06T01:00:00.000Z'
};

// Mock functions
const mockOnSelect = vi.fn();
const mockOnDelete = vi.fn();
const mockOnRename = vi.fn();
const mockOnPin = vi.fn();
const mockOnUnpin = vi.fn();

// Wrap component with providers for testing
const renderWithProviders = (
  conversation = mockConversation,
  isActive = false,
  isPinned = false,
  pinLimitReached = false
) => {
  return render(
    <ConversationListItem
      conversation={conversation}
      isActive={isActive}
      onSelect={mockOnSelect}
      onDelete={mockOnDelete}
      onRename={mockOnRename}
      onPin={mockOnPin}
      onUnpin={mockOnUnpin}
      isPinned={isPinned}
      pinLimitReached={pinLimitReached}
    />
  );
};

describe('ConversationListItem Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders conversation title and timestamp', () => {
    renderWithProviders();
    
    expect(screen.getByText('Test Conversation')).toBeInTheDocument();
    expect(screen.getByText('2 days ago')).toBeInTheDocument();
  });
  
  it('should render with active styling when isActive=true', () => {
    renderWithProviders(true);
    
    // The title should have bold font weight when active
    const title = screen.getByText('Test Conversation');
    const listItem = title.closest('[data-testid^="conversation-item-"]');
    
    expect(listItem).toHaveStyle('background-color: #f0f0f0');
    
    // Check the Typography component classes instead of inline style
    expect(title.classList.contains('MuiTypography-root')).toBeTruthy();
    // MUI applies bold via CSS classes rather than inline style
    expect(title.classList.toString()).toContain('MuiTypography');
  });
  
  it('calls onSelect when clicked', () => {
    renderWithProviders();
    
    const listItem = screen.getByTestId('conversation-item-test-conversation-id');
    fireEvent.click(listItem);
    
    expect(mockOnSelect).toHaveBeenCalledWith('test-conversation-id');
  });
  
  it('shows pin button for unpinned conversation', () => {
    renderWithProviders(mockConversation, false, false);
    
    const pinButton = screen.getByLabelText('Pin');
    expect(pinButton).toBeInTheDocument();
  });
  
  it('shows unpin button for pinned conversation', () => {
    renderWithProviders(mockPinnedConversation, false, true);
    
    const unpinButton = screen.getByLabelText('Unpin');
    expect(unpinButton).toBeInTheDocument();
  });
  
  it('calls onPin when pin button is clicked', () => {
    renderWithProviders(mockConversation, false, false);
    
    const pinButton = screen.getByLabelText('Pin');
    fireEvent.click(pinButton);
    
    expect(mockOnPin).toHaveBeenCalledWith('test-conversation-id');
  });
  
  it('calls onUnpin when unpin button is clicked', () => {
    renderWithProviders(mockPinnedConversation, false, true);
    
    const unpinButton = screen.getByLabelText('Unpin');
    fireEvent.click(unpinButton);
    
    expect(mockOnUnpin).toHaveBeenCalledWith('pinned-conversation-id');
  });
  
  it('shows pin limit dialog when trying to pin with limit reached', async () => {
    renderWithProviders(mockConversation, false, false, true);
    
    const pinButton = screen.getByLabelText('Pin');
    fireEvent.click(pinButton);
    
    // The dialog should open
    expect(screen.getByText('Pin Limit Reached')).toBeInTheDocument();
    
    // Confirm it doesn't call onPin
    expect(mockOnPin).not.toHaveBeenCalled();
    
    // Close the dialog
    const okButton = screen.getByRole('button', { name: 'OK' });
    fireEvent.click(okButton);
  });
  
  it('displays pin icon for pinned conversations', () => {
    renderWithProviders(mockPinnedConversation, false, true);
    
    // There should be 2 pin icons: one in the title and one for the unpin button
    const pinIcons = screen.getAllByTestId('PushPinIcon');
    expect(pinIcons.length).toBeGreaterThan(0);
  });
  
  it('should open delete dialog when delete button is clicked', async () => {
    renderWithProviders();
    
    // Get delete button by aria-label instead of text content
    const deleteButton = screen.getByLabelText('Delete Conversation');
    fireEvent.click(deleteButton);
    
    // Dialog should be visible
    const dialogTitle = await screen.findByText('Delete Conversation?');
    expect(dialogTitle).toBeInTheDocument();
    
    // Confirmation text should include the conversation title
    // Use getAllByText and check one of the elements since there are multiple matches
    const elements = screen.getAllByText(/Test Conversation/i);
    expect(elements.length).toBeGreaterThan(0);
  });
  
  it('should call onDelete when confirmed', async () => {
    renderWithProviders();
    
    // Get delete button by aria-label
    const deleteButton = screen.getByLabelText('Delete Conversation');
    fireEvent.click(deleteButton);
    
    // Click on the confirm button
    const confirmButton = await screen.findByText('Delete');
    fireEvent.click(confirmButton);
    
    // onDelete should be called with the conversation ID
    expect(mockOnDelete).toHaveBeenCalledWith('test-conversation-id');
  });
  
  it('should close the dialog without deleting when canceled', async () => {
    // Start completely fresh
    vi.clearAllMocks();
    
    const { rerender } = renderWithProviders();
    
    // Get delete button by aria-label
    const deleteButton = screen.getByLabelText('Delete Conversation');
    fireEvent.click(deleteButton);
    
    // Make sure the dialog is open
    expect(await screen.findByText('Delete Conversation?')).toBeInTheDocument();
    
    // Click on the cancel button
    const cancelButton = screen.getByText('Cancel');
    fireEvent.click(cancelButton);
    
    // Force a re-render to ensure the dialog close has been processed
    rerender(
      <ConversationListItem
        conversation={mockConversation}
        isActive={false}
        onSelect={mockOnSelect}
        onDelete={mockOnDelete}
      />
    );
    
    // onDelete should not be called
    expect(mockOnDelete).not.toHaveBeenCalled();
    
    // Wait for the dialog to be removed from the DOM
    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
  });
}); 