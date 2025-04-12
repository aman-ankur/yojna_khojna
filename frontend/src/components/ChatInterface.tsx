import { useState, useRef, useEffect } from 'react';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Avatar from '@mui/material/Avatar';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import { blue, grey } from '@mui/material/colors';
import IconButton from '@mui/material/IconButton';
import InputAdornment from '@mui/material/InputAdornment';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import AddPhotoAlternateIcon from '@mui/icons-material/AddPhotoAlternate';
import SendIcon from '@mui/icons-material/Send';
import Button from '@mui/material/Button';

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
      
      // Transform the backend history (array of arrays) to frontend format (array of objects)
      const formattedMessages: Message[] = response.updated_history.flatMap(
        ([humanMsg, aiMsg]) => [
          { role: 'user', content: humanMsg },
          { role: 'assistant', content: aiMsg },
        ]
      );
      
      setMessages(formattedMessages);
      
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
    <Paper elevation={0} sx={{ p: 2, bgcolor: 'background.paper' }}>
      <Stack spacing={2} sx={{ height: '70vh' }}>
        {/* Chat messages display area */}
        <Box
          sx={{
            flexGrow: 1,
            overflowY: 'auto',
            p: 2,
            borderRadius: 1,
            bgcolor: 'background.default'
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
                      bgcolor: message.role === 'user' ? 'background.paper' : '#e3f2fd',
                      maxWidth: '80%',
                      border: message.role === 'user' ? `1px solid ${grey[300]}` : 'none',
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

        {/* Input area - Redesigned */}
        <Paper
          component="form"
          onSubmit={handleSubmit}
          elevation={1} // Subtle elevation like inspiration
          sx={{
            p: 1, // Padding around the input area
            mt: 'auto',
            borderRadius: 2, // Rounded corners
            bgcolor: 'background.paper' // Ensure paper background
          }}
        >
          <Stack spacing={1}>
            <TextField
              fullWidth
              variant="standard"
              size="small"
              placeholder="Ask whatever you want.... (आप कुछ भी पूछ सकते हैं...)" // Updated placeholder
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
              multiline // Allow multiple lines like inspiration
              maxRows={4} // Limit expansion
              InputProps={{
                disableUnderline: true,
                sx: {
                  borderRadius: 2,
                  p: 1,
                  bgcolor: 'action.hover'
                },
              }}
            />
            {/* Buttons below input, similar to inspiration */}
            {/* Row containing action buttons and send button */}
            <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between">
              {/* Left-aligned action buttons */}
              <Stack direction="row" spacing={1}>
                <Button
                  size="small"
                  startIcon={<AttachFileIcon />}
                  aria-label="add attachment"
                  disabled={isLoading}
                  sx={{ textTransform: 'none', color: 'text.secondary' }} // Match inspiration style
                >
                  Add Attachment
                </Button>
                <Button
                  size="small"
                  startIcon={<AddPhotoAlternateIcon />}
                  aria-label="use image"
                  disabled={isLoading}
                  sx={{ textTransform: 'none', color: 'text.secondary' }} // Match inspiration style
                >
                  Use Image
                </Button>
                {/* TODO: Add Voice Input Icon Button here? */}
              </Stack>

              {/* Right-aligned Send Button */}
              <Button
                variant="contained"
                color="secondary"
                type="submit"
                disabled={isLoading || !input.trim()}
                endIcon={isLoading ? <LoadingIndicator size={16} color="inherit" /> : <SendIcon />}
                sx={{
                  minWidth: 'auto', // Allow button to size naturally
                  px: 2 // Add some padding
                }}
              >
                {/* Hide text when loading to prevent layout shift */}
                {!isLoading && 'Send'}
              </Button>
            </Stack>
          </Stack>
        </Paper>
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