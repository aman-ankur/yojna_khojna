import { FC } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { useLanguage } from './LanguageToggle';
import LanguageToggle from './LanguageToggle';

interface WelcomeHeaderProps {
  userName?: string;
}

const WelcomeHeader: FC<WelcomeHeaderProps> = ({ userName }) => {
  const { t, language } = useLanguage();
  const displayName = userName || "नागरिक";
  
  return (
    <Box sx={{ 
      padding: '40px 40px 20px 40px',
      textAlign: 'center',
      position: 'relative'
    }}>
      {/* Language toggle in top-right corner */}
      <Box sx={{ position: 'absolute', top: 16, right: 16 }}>
        <LanguageToggle />
      </Box>
      
      <Typography variant="h3" component="h1" sx={{ 
        fontWeight: 500,
        fontSize: '2.5rem',
        mb: 2
      }}>
        {t.welcome}{' '}
        <Box 
          component="span" 
          sx={{ 
            background: 'linear-gradient(90deg, #C159AB 0%, #8667D0 30%)',
            WebkitBackgroundClip: 'text',
            backgroundClip: 'text',
            color: 'transparent',
            fontWeight: 500
          }}
        >
          {displayName}
        </Box>
      </Typography>
      
      <Typography variant="h4" sx={{ 
        fontSize: '1.8rem',
        mb: 2
      }}>
        <Box 
          component="span" 
          sx={{ 
            background: 'linear-gradient(90deg, #9D67B7 0%, #6952D2 100%)',
            WebkitBackgroundClip: 'text',
            backgroundClip: 'text',
            color: 'transparent',
            fontWeight: 500
          }}
        >
          {t.question}
        </Box>
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ 
        mb: 4,
        fontSize: '1rem',
        maxWidth: '600px',
        mx: 'auto'
      }}>
        {t.subtitle}
      </Typography>
    </Box>
  );
};

export default WelcomeHeader; 