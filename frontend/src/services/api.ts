import axios from 'axios';

// Define API URL (could be moved to env variables later)
const API_URL = 'http://localhost:8000';

// Define types
export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  question: string;
  chat_history: Message[];
}

export interface ChatResponse {
  answer: string;
  updated_history: Message[];
}

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Chat API functions
export const chatService = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    try {
      const response = await api.post<ChatResponse>('/chat', request);
      return response.data;
    } catch (error) {
      console.error('API error:', error);
      throw error;
    }
  }
};

export default api; 