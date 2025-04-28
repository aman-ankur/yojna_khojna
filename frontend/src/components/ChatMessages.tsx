import { FC, ReactNode, useState } from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Avatar from '@mui/material/Avatar';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemIcon from '@mui/material/ListItemIcon';
import CircleIcon from '@mui/icons-material/Circle';

import { Message } from '../services/api';
import SuggestedQuestions, { SuggestedQuestion } from './SuggestedQuestions';
import { useSuggestions } from '../hooks/useSuggestions';

interface ChatMessagesProps {
  messages: Message[];
  isLoading?: boolean;
  onSendMessage: (message: string) => void;
}

const ChatMessages: FC<ChatMessagesProps> = ({ messages, isLoading = false, onSendMessage }) => {
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

  // Safe function to handle question clicks
  const handleQuestionClick = (question: string) => {
    // Type check to make sure onSendMessage is a function before calling it
    if (typeof onSendMessage === 'function') {
      onSendMessage(question);
    } else {
      console.error('onSendMessage is not a function');
    }
  };

  return (
    <Box sx={{ 
      flex: 1, 
      overflow: 'auto',
      padding: '20px 40px',
      display: 'flex',
      flexDirection: 'column',
      gap: 3
    }}>
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
        <Box key={index}>
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
  );
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
        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>{content}</Typography>
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