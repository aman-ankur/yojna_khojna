import { useState, useEffect, useCallback, useRef } from 'react';
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
  
  // Track whether the component has been mounted before
  const initialLoadRef = useRef(true);
  
  // Flag to track page loads vs tab visibility changes
  const [isInitialPageLoad] = useState(true);
  
  // Reference for tracking event timestamps to prevent event loops
  const lastEventTimeRef = useRef(0);
  const eventDebounceTime = 500; // ms

  // Load the current conversation
  const loadCurrentConversation = useCallback(() => {
    setLoading(true);
    try {
      // Initialize service if needed
      conversationService.initialize();
      
      // Get current conversation, ensuring one exists
      // Only use ensureCurrentConversation on initial page load
      let conversation;
      if (initialLoadRef.current) {
        console.log("Initial page load - ensuring current conversation");
        conversation = conversationService.ensureCurrentConversation();
        initialLoadRef.current = false;
      } else {
        console.log("Not initial load - getting current conversation");
        // For tab switching or other re-focus events, just get the current conversation
        conversation = conversationService.getCurrentConversation();
        // If somehow there's no conversation, create one
        if (!conversation) {
          conversation = conversationService.create();
        }
      }
      
      setCurrentConversation(conversation);
      setError(null);
    } catch (err) {
      console.error('Error loading current conversation:', err);
      setError('Failed to load conversation');
    } finally {
      setLoading(false);
    }
  }, []);

  // Handle visibility change events (tab switching)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        // When coming back to the tab, just refresh the current conversation
        console.log("Tab became visible again - loading existing conversation");
        
        // Get the current conversation without creating a new one
        try {
          const currentId = localStorage.getItem('yk_current_conversation');
          if (currentId) {
            const conversation = conversationService.getById(currentId);
            if (conversation) {
              console.log("Loaded existing conversation:", conversation.id);
              setCurrentConversation(conversation);
            }
          }
        } catch (error) {
          console.error("Error loading conversation on tab visibility change:", error);
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  // Setup storage event listener for cross-tab sync and custom events
  useEffect(() => {
    // This will trigger when localStorage changes in any tab
    const handleStorageChange = (event: StorageEvent) => {
      if (event.key?.includes('yk_')) {
        console.log('Storage changed, checking if refresh needed:', event.key);
        
        // Check if we need to refresh based on the key
        if (event.key.includes('CURRENT_CONVERSATION')) {
          const now = Date.now();
          if (now - lastEventTimeRef.current > eventDebounceTime) {
            lastEventTimeRef.current = now;
            
            // Just get the current conversation without creating a new one
            try {
              const currentId = localStorage.getItem('yk_current_conversation');
              if (currentId) {
                const conversation = conversationService.getById(currentId);
                if (conversation) {
                  setCurrentConversation(conversation);
                }
              }
            } catch (error) {
              console.error("Error loading conversation on storage change:", error);
            }
          } else {
            console.log('Debouncing event - too soon after last event');
          }
        }
      }
    };

    // Handle custom conversation change events
    const handleConversationChange = (event: CustomEvent<{ type: string, conversationId: string }>) => {
      console.log('Conversation change event received:', event.detail);
      
      const now = Date.now();
      if (now - lastEventTimeRef.current > eventDebounceTime) {
        lastEventTimeRef.current = now;
        
        // For 'create' or 'switch' events, directly set the conversation without calling loadCurrentConversation
        try {
          const { type, conversationId } = event.detail;
          if (conversationId) {
            const conversation = conversationService.getById(conversationId);
            if (conversation) {
              console.log(`Setting conversation from ${type} event:`, conversation.id);
              setCurrentConversation(conversation);
            }
          }
        } catch (error) {
          console.error("Error handling conversation change event:", error);
        }
      } else {
        console.log('Debouncing event - too soon after last event');
      }
    };

    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('yk_conversation_change', handleConversationChange as EventListener);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('yk_conversation_change', handleConversationChange as EventListener);
    };
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
    console.log("createNewConversation called");
    setLoading(true);
    try {
      // Create the new conversation
      const newConversation = conversationService.create();
      console.log("New conversation created:", newConversation);
      
      // Make sure the new conversation is set as the current one in localStorage
      conversationService.setCurrentConversation(newConversation.id);
      
      // Update our local state with the new conversation
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