import React from 'react';
import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';
import Typography from '@mui/material/Typography';
import Tooltip from '@mui/material/Tooltip';
import { keyframes } from '@mui/system';

// Define fade-in animation
const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

export interface SuggestedQuestion {
  id: string;
  text: string;
}

interface SuggestedQuestionsProps {
  suggestions: SuggestedQuestion[];
  onQuestionClick: (question: string) => void;
  isLoading?: boolean;
}

/**
 * SuggestedQuestions component displays 3-5 relevant follow-up questions
 * after each assistant response as horizontal scrollable chips.
 */
const SuggestedQuestions: React.FC<SuggestedQuestionsProps> = ({
  suggestions,
  onQuestionClick,
  isLoading = false,
}) => {
  if (isLoading) {
    return (
      <Box sx={{ mt: 2, mb: 1 }}>
        <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
          Generating suggestions...
        </Typography>
      </Box>
    );
  }

  if (!suggestions || suggestions.length === 0) {
    return null;
  }

  // Safe click handler with type checking
  const handleClick = (question: string) => {
    if (typeof onQuestionClick === 'function') {
      onQuestionClick(question);
    } else {
      console.error('Question click handler is not a function');
    }
  };

  // Function to truncate text for display
  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <Box
      sx={{
        display: 'flex',
        overflowX: 'auto',
        pb: 1,
        pt: 1,
        mt: 2,
        mb: 1,
        '&::-webkit-scrollbar': {
          height: '4px',
        },
        '&::-webkit-scrollbar-track': {
          background: 'rgba(0,0,0,0.05)',
        },
        '&::-webkit-scrollbar-thumb': {
          background: 'rgba(0,0,0,0.15)',
          borderRadius: '4px',
        },
        animation: `${fadeIn} 0.3s ease-out forwards`,
      }}
    >
      {suggestions.map((suggestion) => {
        // Pre-truncate the text for display
        const displayText = truncateText(suggestion.text, 30);
        
        return (
          <Tooltip 
            key={suggestion.id} 
            title={suggestion.text}
            placement="top"
            arrow
            PopperProps={{
              sx: {
                '& .MuiTooltip-tooltip': {
                  fontSize: '14px',
                  padding: '8px 12px',
                  maxWidth: '300px',
                }
              }
            }}
          >
            <Chip
              label={displayText}
              onClick={() => handleClick(suggestion.text)}
              sx={{
                mx: 0.5,
                my: 0.5,
                bgcolor: 'rgba(105, 82, 210, 0.05)',
                border: '1px solid rgba(105, 82, 210, 0.1)',
                '&:hover': {
                  bgcolor: 'rgba(105, 82, 210, 0.1)',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                  cursor: 'pointer'
                },
                borderRadius: '16px',
                fontSize: '0.85rem',
                flexShrink: 0,
                // Set fixed width instead of max-width to ensure consistency
                width: { xs: '180px', sm: '220px', md: '250px' },
                height: 'auto',
                '& .MuiChip-label': {
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  display: 'block',
                  padding: '8px 4px',
                },
                fontWeight: 'normal',
                transition: 'all 0.2s ease',
              }}
            />
          </Tooltip>
        );
      })}
    </Box>
  );
};

export default SuggestedQuestions; 