import React from 'react';
import { Box, Card, CardActionArea, CardContent, Chip, Typography } from '@mui/material';
import { alpha } from '@mui/material/styles';
import { Scheme, getCategoryColor } from '../../services/schemeService';

interface SchemeCardProps {
  scheme: Scheme;
  onClick: (scheme: Scheme) => void;
}

// Helper function to get card colors
const getCardColors = (category: string) => {
  const mainColor = getCategoryColor(category);
  const bgColor = alpha(mainColor, 0.1); // Create a lighter version for background
  return { mainColor, bgColor };
};

const SchemeCard: React.FC<SchemeCardProps> = ({ scheme, onClick }) => {
  const { mainColor, bgColor } = getCardColors(scheme.category);
  
  return (
    <Card 
      sx={{ 
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        borderRadius: 2,
        boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        overflow: 'hidden',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-3px)',
          boxShadow: '0 4px 12px rgba(0,0,0,0.12)',
        },
        backgroundColor: bgColor,
        border: `1px solid ${alpha(mainColor, 0.2)}`
      }}
    >
      <CardActionArea 
        onClick={() => onClick(scheme)}
        sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'flex-start',
          height: '100%',
          padding: 0
        }}
      >
        <Box 
          sx={{ 
            width: '100%', 
            height: '6px', 
            background: `linear-gradient(90deg, ${mainColor} 0%, ${alpha(mainColor, 0.6)} 100%)` 
          }} 
        />
        <CardContent sx={{ width: '100%', flexGrow: 1, p: 2 }}>
          <Chip 
            label={scheme.category} 
            size="small" 
            sx={{ 
              mb: 1.5, 
              backgroundColor: alpha(mainColor, 0.08),
              color: mainColor,
              fontWeight: 500,
              borderRadius: 1
            }} 
          />
          <Typography variant="h6" component="h2" gutterBottom sx={{ 
            fontWeight: 600,
            fontSize: '1.1rem', 
            color: 'text.primary',
            lineHeight: 1.3 
          }}>
            {scheme.name}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5, height: '3em', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {scheme.description}
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ mt: 'auto', display: 'block' }}>
            {scheme.ministryDepartment}
          </Typography>
        </CardContent>
      </CardActionArea>
    </Card>
  );
};

export default SchemeCard; 