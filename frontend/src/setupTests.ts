import '@testing-library/jest-dom';

// Mock scrollIntoView for jsdom environment
window.Element.prototype.scrollIntoView = vi.fn(); 