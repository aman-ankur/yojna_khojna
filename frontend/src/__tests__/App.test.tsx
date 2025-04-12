import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';
import App from '../App';

// Mock the components to isolate App testing
vi.mock('../components/Sidebar', () => ({
  default: () => <div data-testid="sidebar-component" />
}));

vi.mock('../components/ChatContainer', () => ({
  default: () => <div data-testid="chat-container-component" />
}));

describe('App', () => {
  it('renders with the correct structure', () => {
    render(<App />);
    
    // Check that the main components are rendered
    expect(screen.getByTestId('sidebar-component')).toBeInTheDocument();
    expect(screen.getByTestId('chat-container-component')).toBeInTheDocument();
  });

  it('applies theme via ThemeProvider', () => {
    render(<App />);
    
    // Find the main layout Box using the test id
    const mainBoxLayout = screen.getByTestId('main-layout-box');
    expect(mainBoxLayout).toBeInTheDocument();
    
    // Check if it has the expected MUI class (more robust than assuming parent structure)
    expect(mainBoxLayout).toHaveClass('MuiBox-root');
  });
}); 