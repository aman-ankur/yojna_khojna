import { FC, useState, useRef, useEffect } from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';

import WelcomeHeader from './WelcomeHeader';
import SuggestedPrompts from './SuggestedPrompts';
import ChatInput from './ChatInput';
import ChatMessages from './ChatMessages';
import { chatService, Message as ApiMessage } from '../services/api';
import { useLanguage } from './LanguageToggle';
import useCurrentConversation from '../hooks/useCurrentConversation';

interface ChatContainerProps {
  userName?: string;
}

const ChatContainer: FC<ChatContainerProps> = ({ userName }) => {
  const { t } = useLanguage();
  
  // Get the current conversation
  const { 
    currentConversation, 
    loading: conversationLoading, 
    error: conversationError,
    addMessage,
    refreshCurrentConversation
  } = useCurrentConversation();
  
  // Local state
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Derive conversation started from current conversation
  const conversationStarted = currentConversation?.messages && currentConversation.messages.length > 0;

  // Extract messages for display
  const messages = currentConversation?.messages?.map(msg => ({
    role: msg.role,
    content: msg.content
  })) || [];

  // Add debug logging for conversation changes
  useEffect(() => {
    console.log(`🔄 ChatContainer: conversation changed to: ${currentConversation?.id}`);
    console.log(`Messages count: ${messages.length}`);
  }, [currentConversation?.id, messages.length]);

  // Auto scroll to bottom of messages
  useEffect(() => {
    if (messagesEndRef.current && messages.length > 0) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isLoading]);

  // Start conversation from suggested prompt
  const handlePromptClick = (promptText: string) => {
    sendMessage(promptText);
  };
  
  // Handle sending message
  const sendMessage = async (text: string) => {
    if (!text.trim() || !currentConversation) return;
    
    // Add user message to the current conversation
    addMessage({
      role: 'user',
      content: text
    });
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Transform conversation history for backend
      const backendHistory: [string, string][] = [];
      const conversationMessages = currentConversation.messages;
      
      for (let i = 0; i < conversationMessages.length - 1; i += 2) {
        // Ensure we have a pair of user and assistant messages
        if (
          conversationMessages[i]?.role === 'user' && 
          conversationMessages[i+1]?.role === 'assistant'
        ) {
          backendHistory.push([
            conversationMessages[i].content, 
            conversationMessages[i+1].content
          ]);
        }
      }

      const response = await chatService.sendMessage({
        question: text,
        chat_history: backendHistory as any
      });
      
      // Add assistant response to the conversation
      addMessage({
        role: 'assistant',
        content: response.answer
      });

    } catch (err) {
      console.error('Error communicating with the backend:', err);
      setError(t.error);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle image upload (placeholder)
  const handleImageUpload = async (file: File) => {
    console.log('Image upload:', file.name);
  };
  
  return (
    <Box
      className="chat-outer-container"
      sx={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column',
        height: '100%',
        maxWidth: '1100px',
        width: '100%',
        mx: 'auto',
      }}
    >
      {/* Main chat area with message display and input */}
      <Box 
        className="chat-scroll-container"
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          border: '1px solid rgba(0,0,0,0.12)',
          borderRadius: '12px',
          overflow: 'hidden',
          height: '100%',
        }}
      >
        {/* Content area (welcome or messages) */}
        <Box 
          className="chat-content-area"
          sx={{ 
            flex: 1,
            height: 'calc(100% - 60px)', // Reserve space for input
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden', // Only messages container should scroll
            position: 'static', // Changed from relative to avoid positioning issues
          }}
        >
          {!conversationStarted ? (
            // Welcome view with prompts
            <Box sx={{ 
              height: '100%',
              overflow: 'auto',
              padding: '20px',
            }}>
              <WelcomeHeader userName={userName} />
              <SuggestedPrompts onPromptClick={handlePromptClick} />
            </Box>
          ) : (
            // Chat messages - this is the only scrollable container
            <ChatMessages 
              messages={messages} 
              isLoading={isLoading} 
              onSendMessage={sendMessage}
            />
          )}
        </Box>
        
        {/* Reference for scrolling to bottom */}
        <div ref={messagesEndRef} />
        
        {/* Chat input shown in both views */}
        <Box 
          className="chat-input-container"
          sx={{
            borderTop: '1px solid rgba(0,0,0,0.08)',
            padding: '10px',
            flexShrink: 0,
          }}
        >
          <ChatInput 
            onSendMessage={sendMessage}
            onImageUpload={handleImageUpload}
            disabled={isLoading || conversationLoading}
            isConversationStarted={!!conversationStarted}
          />
        </Box>
      </Box>
      
      {/* Error Snackbar */}
      <Snackbar
        open={!!error || !!conversationError}
        autoHideDuration={6000}
        onClose={() => {
          setError(null);
        }}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={() => setError(null)} 
          severity="error" 
          sx={{ width: '100%' }}
        >
          {error || conversationError}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ChatContainer; 