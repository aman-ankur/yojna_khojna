import { FC } from 'react';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Card from '@mui/material/Card';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import { useLanguage } from './LanguageToggle';

// Icons
import RefreshIcon from '@mui/icons-material/Refresh';
import PersonIcon from '@mui/icons-material/Person';
import EmailIcon from '@mui/icons-material/Email';
import ArticleIcon from '@mui/icons-material/Article';
import HelpIcon from '@mui/icons-material/Help';

interface SuggestedPromptsProps {
  onPromptClick?: (promptText: string) => void;
}

const SuggestedPrompts: FC<SuggestedPromptsProps> = ({ onPromptClick }) => {
  const { t } = useLanguage();
  
  const prompts = [
    { icon: <PersonIcon />, text: t.eligibility },
    { icon: <EmailIcon />, text: t.applicationProcess },
    { icon: <ArticleIcon />, text: t.benefits },
    { icon: <HelpIcon />, text: t.govtHelp }
  ];
  
  const handlePromptClick = (promptText: string) => {
    if (onPromptClick) {
      onPromptClick(promptText);
    }
  };
  
  return (
    <Box sx={{ 
      padding: '0 40px 20px 40px',
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center'
    }}>
      <Grid container spacing={3} sx={{ maxWidth: "900px", margin: "0 auto" }}>
        {prompts.map((prompt, index) => (
          <Grid item xs={12} sm={6} key={index}>
            <Card 
              variant="outlined" 
              sx={{ 
                p: 2.5, 
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                '&:hover': { 
                  backgroundColor: 'rgba(0,0,0,0.03)',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 4px 10px rgba(134, 103, 208, 0.1)',
                  borderColor: 'rgba(134, 103, 208, 0.3)'
                },
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                borderRadius: '12px',
                border: '1px solid rgba(0,0,0,0.12)'
              }}
              onClick={() => handlePromptClick(prompt.text)}
            >
              <Box sx={{ 
                mr: 2.5, 
                color: 'primary.main',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                bgcolor: 'rgba(134, 103, 208, 0.1)',
                p: 1.5,
                borderRadius: '12px'
              }}>
                {prompt.icon}
              </Box>
              <Typography variant="body1" fontWeight={500}>{prompt.text}</Typography>
            </Card>
          </Grid>
        ))}
      </Grid>
      
      <Box sx={{ textAlign: 'center', mt: 3 }}>
        <Button 
          startIcon={<RefreshIcon />} 
          color="inherit" 
          size="small"
          sx={{ 
            textTransform: 'none',
            py: 1,
            px: 2,
            borderRadius: '20px',
            '&:hover': {
              backgroundColor: 'rgba(134, 103, 208, 0.08)'
            }
          }}
        >
          {t.refreshSuggestions}
        </Button>
      </Box>
    </Box>
  );
};

export default SuggestedPrompts; 