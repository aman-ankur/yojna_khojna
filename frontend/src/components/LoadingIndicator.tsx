import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import Typography from '@mui/material/Typography';

interface LoadingIndicatorProps {
  text?: string;
}

const LoadingIndicator = ({ text = "Loading..." }: LoadingIndicatorProps) => {
  return (
    <Box 
      sx={{
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        justifyContent: 'center', 
        p: 2 // Adjust padding as needed
      }}
    >
      <CircularProgress size={24} sx={{ mb: 1 }} />
      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
        {text}
      </Typography>
    </Box>
  );
};

export default LoadingIndicator; 