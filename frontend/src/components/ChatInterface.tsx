import { useState, useRef, useEffect } from 'react';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Avatar from '@mui/material/Avatar';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import { blue, grey } from '@mui/material/colors';

import { chatService, Message } from '../services/api';
import LoadingIndicator from './LoadingIndicator';

const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await chatService.sendMessage({
        question: currentInput, // Use the captured input
        chat_history: messages // Send history *before* the new user message
      });
      setMessages(response.updated_history);
    } catch (err) {
      console.error('Error communicating with the backend:', err);
      setError('Failed to get a response. Please try again.');
      // Revert message add on error
      setMessages(prev => prev.slice(0, -1));
      setInput(currentInput); // Restore input field
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Paper elevation={2} sx={{ p: 2 }}>
      <Stack spacing={2} sx={{ height: '70vh' }}>
        {/* Chat messages display area */}
        <Box
          sx={{
            flexGrow: 1,
            overflowY: 'auto',
            p: 2,
            border: `1px solid ${grey[200]}`,
            borderRadius: 1,
            bgcolor: 'grey.50'
          }}
        >
          {messages.length === 0 ? (
            <Typography sx={{ color: 'text.secondary', textAlign: 'center', py: 10 }}>
              Ask a question about government schemes to get started!
            </Typography>
          ) : (
            <Stack spacing={2} sx={{ p: 1 }}>
              {messages.map((message, index) => (
                <Stack
                  key={index}
                  direction="row"
                  spacing={1}
                  justifyContent={message.role === 'user' ? 'flex-end' : 'flex-start'}
                >
                  {message.role === 'assistant' && (
                    <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>A</Avatar>
                  )}
                  <Paper
                    elevation={0}
                    sx={{
                      p: 1.5,
                      borderRadius: 2,
                      bgcolor: message.role === 'user' ? blue[100] : grey[100],
                      maxWidth: '80%',
                      border: `1px solid ${message.role === 'user' ? blue[200] : grey[200]}`
                    }}
                  >
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                      {message.content}
                    </Typography>
                  </Paper>
                  {message.role === 'user' && (
                    <Avatar sx={{ bgcolor: 'primary.dark', width: 32, height: 32 }}>U</Avatar>
                  )}
                </Stack>
              ))}

              {/* Show loading indicator */} 
              {isLoading && (
                 <Stack
                  direction="row"
                  spacing={1}
                  justifyContent={'flex-start'}
                >
                    <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>A</Avatar>
                    <Paper elevation={0} sx={{ p: 1.5, borderRadius: 2, bgcolor: grey[100], border: `1px solid ${grey[200]}` }}>
                      <LoadingIndicator text="Getting answer..." />
                    </Paper>
                 </Stack>
              )}
              <div ref={messagesEndRef} />
            </Stack>
          )}
        </Box>

        {/* Input area */}
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 'auto' }}>
          <Stack direction="row" spacing={1}>
            <TextField
              fullWidth
              variant="outlined"
              size="small"
              placeholder="Type your question here..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
            />
            <Button
              variant="contained"
              type="submit"
              disabled={isLoading || !input.trim()}
            >
              {isLoading ? 'Sending...' : 'Send'}
            </Button>
          </Stack>
        </Box>
      </Stack>
      
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
    </Paper>
  );
};

export default ChatInterface; 