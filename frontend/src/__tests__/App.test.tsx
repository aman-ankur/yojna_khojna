import { render, screen } from '@testing-library/react';
import App from '../App';

describe('App', () => {
  it('renders the main heading', () => {
    render(<App />);
    expect(screen.getByRole('heading', { level: 1, name: /Yojna Khojna/i })).toBeInTheDocument();
  });

  it('renders the chat interface placeholder text', () => {
    render(<App />);
    expect(screen.getByText(/Ask a question about government schemes to get started!/i)).toBeInTheDocument();
  });

  it('renders the chat input field', () => {
    render(<App />);
    expect(screen.getByPlaceholderText(/Type your question here.../i)).toBeInTheDocument();
  });
}); 