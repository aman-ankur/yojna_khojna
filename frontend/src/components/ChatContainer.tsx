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
    addMessage 
  } = useCurrentConversation();
  
  // Local state
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Derive conversation started from current conversation
  const conversationStarted = currentConversation?.messages?.length > 0;

  // Extract messages for display
  const messages = currentConversation?.messages?.map(msg => ({
    role: msg.role,
    content: msg.content
  })) || [];

  // Auto scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
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
    <Box sx={{ 
      flex: 1, 
      display: 'flex', 
      flexDirection: 'column',
      height: '100%',
      maxWidth: '1100px',
      width: '100%',
      mx: 'auto',
      position: 'relative'
    }}>
      {/* Paper container to add border around the entire chat area */}
      <Paper 
        elevation={0}
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          border: '1px solid rgba(0,0,0,0.12)',
          borderRadius: '12px',
          overflow: 'hidden',
          height: '100%'
        }}
      >
        {/* Conditional rendering based on conversation state */}
        {!conversationStarted ? (
          // Welcome view with prompts
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column',
            flex: 1,
            overflow: 'auto'
          }}>
            <WelcomeHeader userName={userName} />
            <SuggestedPrompts onPromptClick={handlePromptClick} />
          </Box>
        ) : (
          // Conversation view with messages
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column',
            flex: 1,
            overflow: 'hidden'
          }}>
            <ChatMessages 
              messages={messages} 
              isLoading={isLoading} 
              onSendMessage={sendMessage}
            />
          </Box>
        )}
        
        {/* Reference for scrolling to bottom */}
        <div ref={messagesEndRef} />
        
        {/* Chat input shown in both views */}
        <ChatInput 
          onSendMessage={sendMessage}
          onImageUpload={handleImageUpload}
          disabled={isLoading || conversationLoading}
          isConversationStarted={!!conversationStarted}
        />
      </Paper>
      
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