import { FC, useState, useRef } from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import InputBase from '@mui/material/InputBase';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import CircularProgress from '@mui/material/CircularProgress';
import Tooltip from '@mui/material/Tooltip';
import { useLanguage } from './LanguageToggle';

// Icons
import SendIcon from '@mui/icons-material/Send';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import ImageIcon from '@mui/icons-material/Image';
import CameraAltIcon from '@mui/icons-material/CameraAlt';
import CloseIcon from '@mui/icons-material/Close';

interface ChatInputProps {
  onSendMessage?: (text: string) => void;
  onImageUpload?: (file: File) => void;
  placeholder?: string;
  disabled?: boolean;
  isConversationStarted?: boolean;
}

const ChatInput: FC<ChatInputProps> = ({ 
  onSendMessage,
  onImageUpload,
  placeholder,
  disabled = false,
  isConversationStarted = false
}) => {
  const { t } = useLanguage();
  const [inputValue, setInputValue] = useState<string>('');
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Use the appropriate placeholder based on conversation state
  const placeholderText = placeholder || (isConversationStarted ? t.chatPlaceholder : t.inputPlaceholder);
  
  const handleSend = () => {
    if (inputValue.trim() && onSendMessage) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };
  
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };
  
  // Handle file selection
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    // Create preview
    const reader = new FileReader();
    reader.onload = () => {
      setPreviewUrl(reader.result as string);
      
      // Start upload process
      handleImageUpload(file);
    };
    reader.readAsDataURL(file);
  };
  
  // Handle image upload
  const handleImageUpload = async (file: File) => {
    setIsUploading(true);
    
    try {
      // Here you would upload the image to your server
      if (onImageUpload) {
        await onImageUpload(file);
      } else {
        // Simulate upload delay for demo
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    } catch (error) {
      console.error('Image upload failed', error);
    } finally {
      setIsUploading(false);
    }
  };
  
  // Clear selected image
  const handleClearImage = () => {
    setPreviewUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };
  
  return (
    <Box sx={{ 
      padding: '16px 24px',
      borderTop: '1px solid rgba(0,0,0,0.12)',
      backgroundColor: '#fff'
    }}>
      {/* Image preview if available */}
      {previewUrl && (
        <Box sx={{ 
          position: 'relative', 
          mt: 1, 
          mb: 1,
          width: 'fit-content'
        }}>
          <img 
            src={previewUrl} 
            alt="Preview" 
            style={{ 
              maxHeight: '120px', 
              maxWidth: '200px',
              borderRadius: '8px'
            }} 
          />
          <IconButton
            size="small"
            sx={{
              position: 'absolute',
              top: -12,
              right: -12,
              backgroundColor: 'rgba(0,0,0,0.7)',
              color: 'white',
              '&:hover': {
                backgroundColor: 'rgba(0,0,0,0.8)',
              }
            }}
            onClick={handleClearImage}
          >
            <CloseIcon fontSize="small" />
          </IconButton>
        </Box>
      )}
      
      <Paper
        elevation={0}
        component="form"
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        sx={{
          p: '8px 12px',
          display: 'flex',
          alignItems: 'center',
          border: '1px solid rgba(0,0,0,0.15)',
          borderRadius: '24px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
        }}
      >
        {/* File input (hidden) */}
        <input
          type="file"
          accept="image/*"
          ref={fileInputRef}
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        
        {/* Attachment button */}
        <Tooltip title={t.attachment}>
          <span>
            <IconButton 
              size="small"
              disabled={disabled || isUploading}
              sx={{ mr: 0.5 }}
            >
              <AttachFileIcon fontSize="small" />
            </IconButton>
          </span>
        </Tooltip>
        
        {/* Image upload button */}
        <Tooltip title={t.uploadImage}>
          <span>
            <IconButton 
              onClick={() => fileInputRef.current?.click()}
              size="small"
              disabled={disabled || isUploading}
              sx={{ mr: 0.5 }}
            >
              <ImageIcon fontSize="small" />
            </IconButton>
          </span>
        </Tooltip>
        
        {/* Text input */}
        <InputBase
          sx={{ 
            ml: 1, 
            flex: 1,
            fontSize: '0.95rem',
            py: 0.5
          }}
          placeholder={placeholderText}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={disabled || isUploading}
          multiline
          maxRows={4}
        />
        
        {/* Character counter */}
        <Typography variant="caption" color="text.secondary" sx={{ mx: 1 }}>
          {inputValue.length}/1000
        </Typography>
        
        {/* Send button */}
        <IconButton 
          sx={{ 
            background: 'linear-gradient(90deg, #9D67B7 0%, #6952D2 100%)',
            color: 'white',
            padding: '10px',
            '&:hover': { 
              background: 'linear-gradient(90deg, #C159AB 0%, #8667D0 100%)',
              boxShadow: '0 2px 5px rgba(133, 102, 208, 0.4)'
            },
            '&.Mui-disabled': { 
              background: 'linear-gradient(90deg, #D8C5E8 0%, #C7C1E8 100%)',
              opacity: 0.8
            },
            transition: 'all 0.2s ease',
            boxShadow: '0 2px 4px rgba(133, 102, 208, 0.25)'
          }}
          disabled={!inputValue.trim() || disabled || isUploading}
          onClick={handleSend}
          type="submit"
          size="medium"
          aria-label="Send"
        >
          <SendIcon />
        </IconButton>
      </Paper>
      
      {/* Upload progress indicator */}
      {isUploading && (
        <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
          <CircularProgress size={16} sx={{ mr: 1 }} />
          <Typography variant="caption" color="text.secondary">
            {t.uploading}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default ChatInput; 