import { useState, useEffect, useCallback } from 'react';
import conversationService, { Conversation } from '../services/conversationService';

/**
 * Custom hook for managing all conversations
 * Provides methods to create, delete, and retrieve conversations
 */
export const useConversations = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load all conversations from localStorage
  const loadConversations = useCallback(() => {
    try {
      // Initialize the service first (ensures user identity exists)
      conversationService.initialize();
      
      // Get all conversations
      const allConversations = conversationService.getAll();
      setConversations(allConversations);
      setError(null);
    } catch (err) {
      console.error('Error loading conversations:', err);
      setError('Failed to load conversations');
    } finally {
      setLoading(false);
    }
  }, []);

  // Create a new conversation
  const createConversation = useCallback(() => {
    try {
      const newConversation = conversationService.create();
      // Update state with the new list including the new conversation
      loadConversations();
      return newConversation;
    } catch (err) {
      console.error('Error creating conversation:', err);
      setError(err instanceof Error ? err.message : 'Failed to create conversation');
      return null;
    }
  }, [loadConversations]);

  // Delete a conversation
  const deleteConversation = useCallback((id: string) => {
    try {
      conversationService.delete(id);
      // Update state without the deleted conversation
      loadConversations();
    } catch (err) {
      console.error('Error deleting conversation:', err);
      setError('Failed to delete conversation');
    }
  }, [loadConversations]);

  // Initialize on mount
  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  return {
    conversations,
    loading,
    error,
    createConversation,
    deleteConversation,
    refreshConversations: loadConversations
  };
};

export default useConversations; 