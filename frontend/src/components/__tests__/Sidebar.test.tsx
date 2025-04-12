import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';
import Sidebar from '../Sidebar';

describe('Sidebar', () => {
  it('renders all navigation icons', () => {
    render(<Sidebar />);
    
    // Check that all expected buttons are rendered
    // We can't easily check the specific icons, but we can check for the buttons
    const buttons = screen.getAllByRole('button');
    
    // Should have at least 6 icon buttons (close, add, search, home, folder, settings)
    expect(buttons.length).toBeGreaterThanOrEqual(6);
  });
  
  it('applies custom styles from sx prop', () => {
    const customStyles = { 
      width: '100px', 
      height: '200px', 
      backgroundColor: 'red' 
    };
    
    const { container } = render(<Sidebar sx={customStyles} />);
    
    // Get the root Box element
    const sidebarElement = container.firstChild as HTMLElement;
    
    // Check that custom styles are applied
    // Note: In a real test, we'd need to use getComputedStyle, but in jsdom this is limited
    expect(sidebarElement).toHaveStyle('width: 100px');
    expect(sidebarElement).toHaveStyle('height: 200px');
  });
}); 