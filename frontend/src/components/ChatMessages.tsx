import { FC, ReactNode, useState, useEffect, useRef, useLayoutEffect } from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Avatar from '@mui/material/Avatar';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemIcon from '@mui/material/ListItemIcon';
import CircleIcon from '@mui/icons-material/Circle';
import DOMPurify from 'dompurify'; // Import DOMPurify for sanitization

import { Message } from '../services/api';
import SuggestedQuestions, { SuggestedQuestion } from './SuggestedQuestions';
import { useSuggestions } from '../hooks/useSuggestions';

interface ChatMessagesProps {
  messages: Message[];
  isLoading?: boolean;
  onSendMessage: (message: string) => void;
}

const ChatMessages: FC<ChatMessagesProps> = ({ messages, isLoading = false, onSendMessage }) => {
  // Reference for the scroll container
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  
  // Track when this component instance was mounted to avoid scroll interference
  const componentIdRef = useRef(`chat_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`);
  
  // Flag to track if we need to force scroll to top
  const needsScrollResetRef = useRef(true);
  
  // Get a unique ID from the first message for debugging
  const conversationId = messages.length > 0 ? 
    messages[0].content.substring(0, 10) : 'empty';
  
  // Get the last question and answer for suggested questions
  const lastQuestion = messages.length > 0 && messages[messages.length - 2]?.role === 'user'
    ? messages[messages.length - 2].content
    : '';
  
  const lastAnswer = messages.length > 0 && messages[messages.length - 1]?.role === 'assistant'
    ? messages[messages.length - 1].content
    : '';

  const { 
    suggestions, 
    isLoading: suggestionsLoading 
  } = useSuggestions(lastQuestion, lastAnswer, messages);

  // Debug logging
  useEffect(() => {
    console.log(`ChatMessages [${componentIdRef.current}] mounted for conversation: ${conversationId}`);
    
    // Set flag to reset scroll on mount
    needsScrollResetRef.current = true;
    
    return () => {
      console.log(`ChatMessages [${componentIdRef.current}] unmounting`);
    };
  }, [conversationId]);

  // Reset scroll when messages reference changes (conversation switch)
  useLayoutEffect(() => {
    // This runs synchronously right after DOM updates
    if (scrollContainerRef.current && needsScrollResetRef.current) {
      console.log(`[CRITICAL FIX] Resetting scroll position for [${componentIdRef.current}]`);
      
      // Direct DOM manipulation approach to ensure scroll works
      const scrollElement = scrollContainerRef.current;
      
      // Force top anchor into view if it exists
      const topAnchor = document.getElementById(`scroll-target-${componentIdRef.current}`);
      if (topAnchor) {
        topAnchor.scrollIntoView({ behavior: 'auto', block: 'start' });
      }
      
      // Forcibly scroll to top
      scrollElement.scrollTop = 0;
      
      // Record that we've attempted a scroll reset
      needsScrollResetRef.current = false;
      
      // Confirm scroll position
      console.log(`Scroll position now: ${scrollElement.scrollTop}`);
    }
  }, [messages]); // Only depend on messages

  // Try scrolling to the first message when conversation changes
  useEffect(() => {
    // Try to scroll to first message specifically
    const attemptScrollToFirstMessage = () => {
      const firstMessageEl = document.getElementById(`first-message-${componentIdRef.current}`);
      if (firstMessageEl && needsScrollResetRef.current) {
        firstMessageEl.scrollIntoView({ behavior: 'auto', block: 'start' });
        console.log(`Attempted to scroll to first message element`);
      }
    };
    
    // Try multiple times with delays
    attemptScrollToFirstMessage();
    const timers = [
      setTimeout(attemptScrollToFirstMessage, 100),
      setTimeout(attemptScrollToFirstMessage, 300),
      setTimeout(attemptScrollToFirstMessage, 800)
    ];
    
    return () => {
      timers.forEach(clearTimeout);
    };
  }, [messages]);  // Re-run when messages change

  // Use scroll event detection to know when the user has manually scrolled
  useEffect(() => {
    if (!scrollContainerRef.current) return;
    
    const scrollElement = scrollContainerRef.current;
    
    // Basic scroll event detection to know if user has scrolled
    const handleScroll = () => {
      // Once user has scrolled, we no longer need to force scroll resets
      if (scrollElement.scrollTop > 5) {
        needsScrollResetRef.current = false;
      }
    };
    
    scrollElement.addEventListener('scroll', handleScroll);
    
    return () => {
      scrollElement.removeEventListener('scroll', handleScroll);
    };
  }, []);  // Only run on mount

  // Safe function to handle question clicks
  const handleQuestionClick = (question: string) => {
    if (typeof onSendMessage === 'function') {
      onSendMessage(question);
    } else {
      console.error('onSendMessage is not a function');
    }
  };

  return (
    <>
      {/* Hidden element at the very top that we can use for scrolling to ensure top visibility */}
      <div 
        id={`scroll-target-${componentIdRef.current}`} 
        style={{ 
          position: 'absolute',
          top: 0,
          left: 0,
          height: 1,
          width: '100%',
          opacity: 0,
          pointerEvents: 'none'
        }}
      />
      
      <Box 
        id={`messages-${componentIdRef.current}`}
        ref={scrollContainerRef}
        className="chat-messages-scrollable"
        sx={{ 
          height: '100%',
          width: '100%',
          overflow: 'auto',
          padding: '20px 40px 100px 40px', // Extra padding at bottom
          display: 'flex',
          flexDirection: 'column',
          gap: 3,
        }}
      >
        {messages.length === 0 && !isLoading && (
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center',
            height: '100%',
            opacity: 0.7
          }}>
            <Typography variant="body1" color="text.secondary">
              Start a conversation to see messages here.
            </Typography>
          </Box>
        )}
        
        {messages.map((message, index) => (
          <Box 
            key={`msg-${index}-${message.role}-${componentIdRef.current}`}
            className={index === 0 ? 'first-message' : ''}
            id={index === 0 ? `first-message-${componentIdRef.current}` : undefined}
          >
            {message.role === 'user' ? (
              <UserMessage content={message.content} />
            ) : (
              <>
                <AssistantMessage content={message.content} />
                {/* Only show suggestions after the last assistant message and when not loading */}
                {index === messages.length - 1 && !isLoading && (
                  <SuggestedQuestions 
                    suggestions={suggestions}
                    onQuestionClick={handleQuestionClick}
                    isLoading={suggestionsLoading}
                  />
                )}
              </>
            )}
          </Box>
        ))}
        
        {isLoading && <TypingIndicator />}
      </Box>
    </>
  );
};

// Function to sanitize HTML to prevent XSS attacks
const sanitizeHtml = (html: string): string => {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p', 'br', 'ul', 'ol', 'li', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
    ALLOWED_ATTR: ['href', 'target', 'rel']
  });
};

// Assistant Message Component
interface MessageProps {
  content: string | ReactNode;
}

export const AssistantMessage: FC<MessageProps> = ({ content }) => (
  <Box sx={{ 
    display: 'flex', 
    alignItems: 'flex-start',
    maxWidth: '85%',
    alignSelf: 'flex-start',
    animation: 'fadeIn 0.3s ease-out forwards',
  }}>
    <Avatar
      sx={{ 
        width: 32, 
        height: 32, 
        mr: 1.5, 
        background: 'linear-gradient(135deg, #9D67B7 0%, #6952D2 100%)',
        fontSize: '14px'
      }}
    >
      Y
    </Avatar>
    <Paper
      elevation={0}
      sx={{
        p: 2,
        backgroundColor: '#f8f8fc',
        borderRadius: '0px 12px 12px 12px',
        border: '1px solid rgba(105, 82, 210, 0.1)',
        boxShadow: '0 1px 3px rgba(105, 82, 210, 0.05)'
      }}
    >
      {typeof content === 'string' ? (
        <Typography 
          variant="body1" 
          component="div"
          sx={{ 
            whiteSpace: 'pre-wrap',
            '& a': { color: 'primary.main' }, // Style links appropriately
            '& strong': { fontWeight: 'bold' } // Ensure strong tags are bold
          }}
          dangerouslySetInnerHTML={{ __html: sanitizeHtml(content) }}
        />
      ) : (
        content
      )}
    </Paper>
  </Box>
);

// User Message Component
export const UserMessage: FC<MessageProps> = ({ content }) => (
  <Box sx={{ 
    display: 'flex', 
    alignItems: 'flex-start',
    maxWidth: '85%',
    ml: 'auto',
    alignSelf: 'flex-end',
    animation: 'fadeIn 0.3s ease-out forwards',
  }}>
    <Paper
      elevation={0}
      sx={{
        p: 2,
        background: 'linear-gradient(90deg, #eeedfa 0%, #f3e6f8 100%)',
        borderRadius: '12px 0px 12px 12px',
        border: '1px solid rgba(193, 89, 171, 0.08)',
      }}
    >
      <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>{content}</Typography>
    </Paper>
    <Avatar
      sx={{ 
        width: 32, 
        height: 32, 
        ml: 1.5, 
        background: 'linear-gradient(135deg, #C159AB 0%, #8667D0 100%)',
        fontSize: '14px'
      }}
    >
      U
    </Avatar>
  </Box>
);

// Typing indicator for the assistant
export const TypingIndicator: FC = () => (
  <Box sx={{ 
    display: 'flex', 
    alignItems: 'center',
    maxWidth: '85%',
    alignSelf: 'flex-start',
    animation: 'fadeIn 0.3s ease-out forwards',
  }}>
    <Avatar
      sx={{ 
        width: 32, 
        height: 32, 
        mr: 1.5, 
        background: 'linear-gradient(135deg, #9D67B7 0%, #6952D2 100%)',
        fontSize: '14px'
      }}
    >
      Y
    </Avatar>
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        p: 1.5,
        backgroundColor: '#f8f8fc',
        borderRadius: '0px 12px 12px 12px',
        border: '1px solid rgba(105, 82, 210, 0.1)',
      }}
    >
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: 0.5 
      }}>
        <Box 
          component="span" 
          sx={{ 
            width: 8, 
            height: 8, 
            borderRadius: '50%', 
            background: 'linear-gradient(135deg, #9D67B7 0%, #6952D2 100%)',
            opacity: 0.4,
            animation: 'pulse 1s infinite',
            animationDelay: '0s',
          }} 
        />
        <Box 
          component="span" 
          sx={{ 
            width: 8, 
            height: 8, 
            borderRadius: '50%', 
            background: 'linear-gradient(135deg, #9D67B7 0%, #6952D2 100%)',
            opacity: 0.4,
            animation: 'pulse 1s infinite',
            animationDelay: '0.2s',
          }} 
        />
        <Box 
          component="span" 
          sx={{ 
            width: 8, 
            height: 8, 
            borderRadius: '50%', 
            background: 'linear-gradient(135deg, #9D67B7 0%, #6952D2 100%)',
            opacity: 0.4,
            animation: 'pulse 1s infinite',
            animationDelay: '0.4s',
          }} 
        />
      </Box>
    </Box>
  </Box>
);

// Define keyframes for animations in the main CSS file or as a global style
// @keyframes pulse {
//   0% { opacity: 0.4; transform: scale(1); }
//   50% { opacity: 1; transform: scale(1.2); }
//   100% { opacity: 0.4; transform: scale(1); }
// }

// @keyframes fadeIn {
//   from { opacity: 0; transform: translateY(10px); }
//   to { opacity: 1; transform: translateY(0); }
// }

export default ChatMessages; 