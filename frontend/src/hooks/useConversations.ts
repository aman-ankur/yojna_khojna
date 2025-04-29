import { useState, useEffect, useCallback } from 'react';
import conversationService, { Conversation } from '../services/conversationService';

/**
 * Custom hook for managing all conversations
 * Provides methods to create, delete, and retrieve conversations
 */
export const useConversations = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [pinnedConversations, setPinnedConversations] = useState<Conversation[]>([]);
  const [unpinnedConversations, setUnpinnedConversations] = useState<Conversation[]>([]);
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
      
      // Split into pinned and unpinned
      const pinned = conversationService.getPinnedConversations();
      const unpinned = conversationService.getUnpinnedConversations();
      
      setPinnedConversations(pinned);
      setUnpinnedConversations(unpinned);
      
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

  // Rename a conversation
  const renameConversation = useCallback((id: string, newTitle: string) => {
    try {
      conversationService.renameConversation(id, newTitle);
      // Update state with the renamed conversation
      loadConversations();
    } catch (err) {
      console.error('Error renaming conversation:', err);
      setError('Failed to rename conversation');
    }
  }, [loadConversations]);
  
  // Pin a conversation
  const pinConversation = useCallback((id: string) => {
    try {
      conversationService.pinConversation(id);
      // Update state with the pinned conversation
      loadConversations();
    } catch (err) {
      console.error('Error pinning conversation:', err);
      setError(err instanceof Error ? err.message : 'Failed to pin conversation');
      throw err; // Re-throw to allow UI to show the error (e.g., max pins reached)
    }
  }, [loadConversations]);
  
  // Unpin a conversation
  const unpinConversation = useCallback((id: string) => {
    try {
      conversationService.unpinConversation(id);
      // Update state with the unpinned conversation
      loadConversations();
    } catch (err) {
      console.error('Error unpinning conversation:', err);
      setError('Failed to unpin conversation');
    }
  }, [loadConversations]);
  
  // Get current pin count
  const getPinnedCount = useCallback(() => {
    return pinnedConversations.length;
  }, [pinnedConversations]);
  
  // Check if pin limit reached
  const isPinLimitReached = useCallback(() => {
    return pinnedConversations.length >= 3;
  }, [pinnedConversations]);

  // Initialize on mount
  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  return {
    conversations,
    pinnedConversations,
    unpinnedConversations,
    loading,
    error,
    createConversation,
    deleteConversation,
    renameConversation,
    pinConversation,
    unpinConversation,
    refreshConversations: loadConversations,
    getPinnedCount,
    isPinLimitReached
  };
};

export default useConversations; 