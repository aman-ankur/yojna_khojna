import { useState, useEffect, useCallback } from 'react';
import conversationService, { 
  Conversation, 
  Message
} from '../services/conversationService';

/**
 * Custom hook for managing the current active conversation
 */
export const useCurrentConversation = () => {
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load the current conversation
  const loadCurrentConversation = useCallback(() => {
    setLoading(true);
    try {
      // Initialize service if needed
      conversationService.initialize();
      
      // Get current conversation, ensuring one exists
      const conversation = conversationService.ensureCurrentConversation();
      setCurrentConversation(conversation);
      setError(null);
    } catch (err) {
      console.error('Error loading current conversation:', err);
      setError('Failed to load conversation');
    } finally {
      setLoading(false);
    }
  }, []);

  // Switch to a different conversation
  const switchConversation = useCallback((id: string) => {
    setLoading(true);
    try {
      const conversation = conversationService.setCurrentConversation(id);
      setCurrentConversation(conversation);
      setError(null);
    } catch (err) {
      console.error('Error switching conversation:', err);
      setError('Failed to switch conversation');
    } finally {
      setLoading(false);
    }
  }, []);

  // Add a message to the current conversation
  const addMessage = useCallback((message: Omit<Message, 'id' | 'timestamp'>) => {
    if (!currentConversation) {
      console.error('No active conversation to add message to');
      setError('No active conversation');
      return;
    }

    try {
      const updatedConversation = conversationService.addMessage(
        currentConversation.id,
        message
      );
      setCurrentConversation(updatedConversation);
    } catch (err) {
      console.error('Error adding message:', err);
      setError('Failed to add message');
    }
  }, [currentConversation]);

  // Create a new conversation and set it as current
  const createNewConversation = useCallback(() => {
    setLoading(true);
    try {
      const newConversation = conversationService.create();
      setCurrentConversation(newConversation);
      setError(null);
      return newConversation;
    } catch (err) {
      console.error('Error creating new conversation:', err);
      setError(err instanceof Error ? err.message : 'Failed to create conversation');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Initialize on mount
  useEffect(() => {
    loadCurrentConversation();
  }, [loadCurrentConversation]);

  return {
    currentConversation,
    loading,
    error,
    switchConversation,
    addMessage,
    createNewConversation,
    refreshCurrentConversation: loadCurrentConversation
  };
};

export default useCurrentConversation; 