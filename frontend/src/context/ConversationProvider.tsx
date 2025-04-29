import { FC, createContext, useContext, ReactNode } from 'react';
import useConversations from '../hooks/useConversations';
import useCurrentConversation from '../hooks/useCurrentConversation';
import { Conversation, Message } from '../services/conversationService';

// Define the context shape
interface ConversationContextType {
  // All conversations
  conversations: Conversation[];
  pinnedConversations: Conversation[];
  unpinnedConversations: Conversation[];
  conversationsLoading: boolean;
  conversationsError: string | null;
  createConversation: () => Conversation | null;
  deleteConversation: (id: string) => void;
  renameConversation: (id: string, newTitle: string) => void;
  pinConversation: (id: string) => void;
  unpinConversation: (id: string) => void;
  isPinLimitReached: () => boolean;
  refreshConversations: () => void;
  
  // Current conversation
  currentConversation: Conversation | null;
  currentConversationLoading: boolean;
  currentConversationError: string | null;
  switchConversation: (id: string) => void;
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  createNewConversation: () => Conversation | null;
  refreshCurrentConversation: () => void;
}

// Create the context
const ConversationContext = createContext<ConversationContextType | undefined>(undefined);

// Context provider props
interface ConversationProviderProps {
  children: ReactNode;
}

// Custom hook to use the context
export const useConversationContext = () => {
  const context = useContext(ConversationContext);
  if (context === undefined) {
    throw new Error('useConversationContext must be used within a ConversationProvider');
  }
  return context;
};

const ConversationProvider: FC<ConversationProviderProps> = ({ children }) => {
  // Use our custom hooks
  const {
    conversations,
    pinnedConversations,
    unpinnedConversations,
    loading: conversationsLoading,
    error: conversationsError,
    createConversation,
    deleteConversation,
    renameConversation,
    pinConversation,
    unpinConversation,
    refreshConversations,
    isPinLimitReached
  } = useConversations();
  
  const {
    currentConversation,
    loading: currentConversationLoading,
    error: currentConversationError,
    switchConversation,
    addMessage,
    createNewConversation,
    refreshCurrentConversation
  } = useCurrentConversation();
  
  // Combine values from both hooks into a single context
  const contextValue: ConversationContextType = {
    // All conversations
    conversations,
    pinnedConversations,
    unpinnedConversations,
    conversationsLoading,
    conversationsError,
    createConversation,
    deleteConversation,
    renameConversation,
    pinConversation,
    unpinConversation,
    isPinLimitReached,
    refreshConversations,
    
    // Current conversation
    currentConversation,
    currentConversationLoading,
    currentConversationError,
    switchConversation,
    addMessage,
    createNewConversation,
    refreshCurrentConversation
  };
  
  return (
    <ConversationContext.Provider value={contextValue}>
      {children}
    </ConversationContext.Provider>
  );
};

export default ConversationProvider; 