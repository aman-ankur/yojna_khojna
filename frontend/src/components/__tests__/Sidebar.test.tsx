import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';
import Sidebar from '../Sidebar';

// Mock the hooks used in Sidebar
vi.mock('../../hooks/useConversations', () => ({
  default: () => ({
    conversations: [],
    loading: false,
    error: null,
    createConversation: vi.fn(),
    deleteConversation: vi.fn(),
    refreshConversations: vi.fn()
  })
}));

vi.mock('../../hooks/useCurrentConversation', () => ({
  default: () => ({
    currentConversation: null,
    loading: false,
    error: null,
    switchConversation: vi.fn(),
    addMessage: vi.fn(),
    createNewConversation: vi.fn(),
    refreshCurrentConversation: vi.fn()
  })
}));

vi.mock('@mui/material/useMediaQuery', () => ({
  default: () => false // Mock as desktop
}));

describe('Sidebar', () => {
  it('renders all navigation icons', () => {
    render(<Sidebar />);
    
    // Check that all expected buttons are rendered
    // We can't easily check the specific icons, but we can check for the buttons
    const buttons = screen.getAllByRole('button');
    
    // Should have at least 5 icon buttons in the collapsed sidebar (menu, add, chat, home, settings)
    expect(buttons.length).toBeGreaterThanOrEqual(5);
  });
  
  it('applies custom styles from sx prop', () => {
    const customStyles = { 
      width: '100px', 
      height: '200px', 
      backgroundColor: 'red' 
    };
    
    const { container } = render(<Sidebar sx={customStyles} />);
    
    // Get the root Box element (now wrapped in a fragment, so we need the first actual element)
    const sidebarElement = container.querySelector('[data-testid="toggle-sidebar"]')
      ?.closest('.MuiBox-root') as HTMLElement;
    
    // Check that custom styles are applied
    expect(sidebarElement).toHaveStyle('width: 100px');
    expect(sidebarElement).toHaveStyle('height: 200px');
  });
}); 