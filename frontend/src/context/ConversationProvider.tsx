import { FC, createContext, useContext, ReactNode } from 'react';
import useConversations from '../hooks/useConversations';
import useCurrentConversation from '../hooks/useCurrentConversation';
import { Conversation, Message } from '../services/conversationService';

// Define the context shape
interface ConversationContextType {
  // All conversations
  conversations: Conversation[];
  conversationsLoading: boolean;
  conversationsError: string | null;
  createConversation: () => Conversation | null;
  deleteConversation: (id: string) => void;
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

// Create context with default values
const ConversationContext = createContext<ConversationContextType>({
  conversations: [],
  conversationsLoading: false,
  conversationsError: null,
  createConversation: () => null,
  deleteConversation: () => {},
  refreshConversations: () => {},
  
  currentConversation: null,
  currentConversationLoading: false,
  currentConversationError: null,
  switchConversation: () => {},
  addMessage: () => {},
  createNewConversation: () => null,
  refreshCurrentConversation: () => {},
});

// Provider component
interface ConversationProviderProps {
  children: ReactNode;
}

const ConversationProvider: FC<ConversationProviderProps> = ({ children }) => {
  // Use our custom hooks
  const {
    conversations,
    loading: conversationsLoading,
    error: conversationsError,
    createConversation,
    deleteConversation,
    refreshConversations
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
    conversationsLoading,
    conversationsError,
    createConversation,
    deleteConversation,
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

// Custom hook for using the conversation context
export const useConversationContext = () => useContext(ConversationContext);

export default ConversationProvider; 