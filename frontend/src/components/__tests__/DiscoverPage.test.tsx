import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi } from 'vitest';
import DiscoverPage from '../schemes/DiscoverPage';
import { useLanguage } from '../LanguageToggle';
import conversationService from '../../services/conversationService';
import { getSchemes } from '../../services/schemeService';

// Mock the dependencies
vi.mock('../LanguageToggle', () => ({
  useLanguage: vi.fn(),
}));

vi.mock('../../services/conversationService', () => ({
  default: {
    create: vi.fn(),
    addMessage: vi.fn(),
    setCurrentConversation: vi.fn(),
  },
}));

vi.mock('../../services/schemeService', () => ({
  getSchemes: vi.fn(),
}));

vi.mock('react-router-dom', () => ({
  ...vi.importActual('react-router-dom'),
  useNavigate: () => vi.fn(),
}));

describe('DiscoverPage Component', () => {
  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks();
    
    // Mock translations
    (useLanguage as jest.Mock).mockReturnValue({
      t: {
        discoverSchemes: 'Discover Schemes',
        discoverSchemesDescription: 'Explore government schemes',
        searchSchemes: 'Search schemes...',
        noSchemesFound: 'No schemes found',
      },
    });
    
    // Mock schemes data
    (getSchemes as jest.Mock).mockResolvedValue([
      {
        id: '1',
        name: 'Test Scheme',
        description: 'Test description',
        category: 'Education',
        ministryDepartment: 'Ministry of Testing',
        eligibility: 'Test eligibility',
        benefits: 'Test benefits',
      },
    ]);
  });
  
  it('renders the discover page with title and description', async () => {
    render(
      <BrowserRouter>
        <DiscoverPage />
      </BrowserRouter>
    );
    
    // Check for title and description
    await waitFor(() => {
      expect(screen.getByText('Discover Schemes')).toBeInTheDocument();
      expect(screen.getByText('Explore government schemes')).toBeInTheDocument();
    });
  });
  
  it('displays schemes when loaded', async () => {
    render(
      <BrowserRouter>
        <DiscoverPage />
      </BrowserRouter>
    );
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.getByText('Test Scheme')).toBeInTheDocument();
    });
  });
  
  it('creates a conversation when a scheme is clicked', async () => {
    // Set up conversation mocks
    const mockConversation = { id: 'test-id' };
    (conversationService.create as jest.Mock).mockReturnValue(mockConversation);
    
    render(
      <BrowserRouter>
        <DiscoverPage />
      </BrowserRouter>
    );
    
    // Wait for schemes to load
    await waitFor(() => {
      expect(screen.getByText('Test Scheme')).toBeInTheDocument();
    });
    
    // Click on the scheme
    fireEvent.click(screen.getByText('Test Scheme'));
    
    // Check if conversation service methods were called correctly
    expect(conversationService.create).toHaveBeenCalled();
    expect(conversationService.addMessage).toHaveBeenCalledWith(
      'test-id', 
      expect.objectContaining({
        role: 'user',
        content: expect.stringContaining('Test Scheme'),
      })
    );
    expect(conversationService.setCurrentConversation).toHaveBeenCalledWith('test-id');
  });
  
  it('filters schemes when a search query is entered', async () => {
    // Mock more schemes to test filtering
    (getSchemes as jest.Mock).mockResolvedValue([
      {
        id: '1',
        name: 'Scholarship Scheme',
        description: 'Education scholarship',
        category: 'Education',
        ministryDepartment: 'Ministry of Education',
        eligibility: 'Students',
        benefits: 'Financial aid',
      },
      {
        id: '2',
        name: 'Healthcare Scheme',
        description: 'Health insurance',
        category: 'Health',
        ministryDepartment: 'Ministry of Health',
        eligibility: 'All citizens',
        benefits: 'Medical coverage',
      },
    ]);
    
    render(
      <BrowserRouter>
        <DiscoverPage />
      </BrowserRouter>
    );
    
    // Wait for all schemes to load
    await waitFor(() => {
      expect(screen.getByText('Scholarship Scheme')).toBeInTheDocument();
      expect(screen.getByText('Healthcare Scheme')).toBeInTheDocument();
    });
    
    // Enter search query
    const searchInput = screen.getByPlaceholderText('Search schemes...');
    fireEvent.change(searchInput, { target: { value: 'health' } });
    
    // Only healthcare scheme should be visible now
    await waitFor(() => {
      expect(screen.getByText('Healthcare Scheme')).toBeInTheDocument();
      expect(screen.queryByText('Scholarship Scheme')).not.toBeInTheDocument();
    });
  });
}); 