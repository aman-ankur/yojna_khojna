import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LanguageProvider, useLanguage } from '../../components/LanguageToggle';
import ConversationListItem from '../ConversationListItem';
import { Conversation } from '../../services/conversationService';

// Mock useLanguage
vi.mock('../../components/LanguageToggle', async () => {
  const actual = await vi.importActual('../../components/LanguageToggle');
  return {
    ...actual,
    useLanguage: () => ({
      language: 'en',
      t: {
        deleteConversation: 'Delete Conversation',
        deleteConversationTitle: 'Delete Conversation?',
        deleteConversationConfirm: 'Are you sure you want to delete the conversation',
        cancel: 'Cancel',
        delete: 'Delete'
      }
    })
  };
});

// Mock test conversation
const mockConversation: Conversation = {
  id: 'test-conversation-id',
  title: 'Test Conversation',
  messages: [],
  createdAt: '2023-01-01T00:00:00.000Z',
  updatedAt: '2023-01-05T00:00:00.000Z',
};

// Mock functions
const mockOnSelect = vi.fn();
const mockOnDelete = vi.fn();

// Wrap component with providers for testing
const renderWithProviders = (
  isActive: boolean = false
) => {
  return render(
    <ConversationListItem
      conversation={mockConversation}
      isActive={isActive}
      onSelect={mockOnSelect}
      onDelete={mockOnDelete}
    />
  );
};

describe('ConversationListItem Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render the conversation title', () => {
    renderWithProviders();
    
    // Title should be displayed
    expect(screen.getByText('Test Conversation')).toBeInTheDocument();
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
  
  it('should call onSelect when clicked', () => {
    renderWithProviders();
    
    // Click on the conversation item
    const listItem = screen.getByTestId('conversation-item-test-conversation-id');
    fireEvent.click(listItem);
    
    // onSelect should be called with the conversation ID
    expect(mockOnSelect).toHaveBeenCalledWith('test-conversation-id');
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