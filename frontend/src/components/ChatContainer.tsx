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
import { chatService, Message } from '../services/api';
import { useLanguage } from './LanguageToggle';

interface ChatContainerProps {
  userName?: string;
}

const ChatContainer: FC<ChatContainerProps> = ({ userName }) => {
  const { t } = useLanguage();
  // State to track if conversation has started
  const [conversationStarted, setConversationStarted] = useState<boolean>(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

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
    if (!text.trim()) return;
    
    // If first message, transition to conversation view
    if (!conversationStarted) {
      setConversationStarted(true);
    }
    
    // Add user message
    const userMessage: Message = { role: 'user', content: text };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await chatService.sendMessage({
        question: text,
        chat_history: messages // Send history before the new user message
      });
      
      // Transform the backend history to frontend format if needed
      // Depending on your backend response structure
      if (Array.isArray(response.updated_history)) {
        setMessages(response.updated_history);
      } else {
        // If the backend doesn't return updated history, add the answer as a new message
        setMessages(prev => [...prev, { role: 'assistant', content: response.answer }]);
      }
    } catch (err) {
      console.error('Error communicating with the backend:', err);
      setError(t.error);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle image upload (placeholder)
  const handleImageUpload = async (file: File) => {
    // Implementation would depend on your backend API
    console.log('Image upload:', file.name);
    // You could upload the image and then reference it in a message
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
            />
          </Box>
        )}
        
        {/* Reference for scrolling to bottom */}
        <div ref={messagesEndRef} />
        
        {/* Chat input shown in both views */}
        <ChatInput 
          onSendMessage={sendMessage}
          onImageUpload={handleImageUpload}
          disabled={isLoading}
          isConversationStarted={conversationStarted}
        />
      </Paper>
      
      {/* Error Snackbar */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setError(null)} severity="error" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ChatContainer; 