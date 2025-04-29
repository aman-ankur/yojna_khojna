import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Chip,
  Stack,
  CircularProgress,
  TextField,
  InputAdornment,
  useMediaQuery,
  useTheme
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import SchemeCard from './SchemeCard';
import { Scheme, SchemeCategory, getSchemes } from '../../services/schemeService';
import { useLanguage } from '../LanguageToggle';
import conversationService from '../../services/conversationService';
import { useNavigate } from 'react-router-dom';

const DiscoverPage: React.FC = () => {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const theme = useTheme();
  
  // Responsive grid columns
  const isXsScreen = useMediaQuery(theme.breakpoints.only('xs'));
  const isSmScreen = useMediaQuery(theme.breakpoints.only('sm'));
  const isMdScreen = useMediaQuery(theme.breakpoints.only('md'));
  
  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [categories, setCategories] = useState<SchemeCategory[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<SchemeCategory | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  // Determine grid columns based on screen size
  const getGridColumns = () => {
    if (isXsScreen) return 1;
    if (isSmScreen) return 2;
    if (isMdScreen) return 3;
    return 4; // lg and above
  };

  // Load schemes data
  useEffect(() => {
    const loadSchemes = async () => {
      try {
        setLoading(true);
        const schemeData = await getSchemes();
        setSchemes(schemeData);
        
        // Extract unique categories
        const uniqueCategories = Array.from(
          new Set(schemeData.map(scheme => scheme.category))
        ) as SchemeCategory[];
        
        setCategories(uniqueCategories);
      } catch (error) {
        console.error('Failed to load schemes:', error);
      } finally {
        setLoading(false);
      }
    };

    loadSchemes();
  }, []);

  // Handle category selection
  const handleCategoryClick = (category: SchemeCategory) => {
    setSelectedCategory(prev => 
      prev === category ? null : category
    );
  };

  // Handle search input
  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
  };

  // Filter schemes based on category and search query
  const filteredSchemes = schemes.filter(scheme => {
    const matchesCategory = !selectedCategory || scheme.category === selectedCategory;
    const matchesSearch = !searchQuery || 
      scheme.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      scheme.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      scheme.ministryDepartment.toLowerCase().includes(searchQuery.toLowerCase());
    
    return matchesCategory && matchesSearch;
  });

  // Handle scheme card click
  const handleSchemeClick = (scheme: Scheme) => {
    // Create new conversation
    const newConversation = conversationService.create();
    
    // Add initial message
    conversationService.addMessage(newConversation.id, {
      role: 'user',
      content: `Tell me about the ${scheme.name} scheme. What are the eligibility criteria, benefits, and how do I apply?`
    });
    
    // Set as current conversation and navigate to chat
    conversationService.setCurrentConversation(newConversation.id);
    navigate('/chat');
  };

  return (
    <Box sx={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      overflow: 'auto'
    }}>
      <Container maxWidth="lg" sx={{ py: 3, flexGrow: 1, display: 'flex', flexDirection: 'column', overflow: 'visible' }}>
        {/* Header Section */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
            {t.discoverSchemes}
          </Typography>
          <Typography variant="body1" color="text.secondary" gutterBottom>
            {t.discoverSchemesDescription}
          </Typography>
          
          {/* Search Box */}
          <TextField
            fullWidth
            placeholder={t.searchSchemes}
            variant="outlined"
            value={searchQuery}
            onChange={handleSearchChange}
            sx={{ mt: 2, mb: 3 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon color="action" />
                </InputAdornment>
              ),
            }}
          />
          
          {/* Category Filters */}
          <Stack 
            direction="row" 
            spacing={1}
            sx={{ 
              mb: 2, 
              flexWrap: 'wrap',
              gap: 1
            }}
          >
            {categories.map(category => (
              <Chip
                key={category}
                label={category}
                onClick={() => handleCategoryClick(category)}
                color={selectedCategory === category ? 'primary' : 'default'}
                variant={selectedCategory === category ? 'filled' : 'outlined'}
                sx={{ mb: 1 }}
              />
            ))}
          </Stack>
        </Box>
        
        {/* Main Content - Scrollable Area */}
        <Box 
          sx={{ 
            flexGrow: 1, 
            '&::-webkit-scrollbar': {
              width: '8px',
            },
            '&::-webkit-scrollbar-track': {
              backgroundColor: 'rgba(0,0,0,0.05)',
            },
            '&::-webkit-scrollbar-thumb': {
              backgroundColor: 'rgba(0,0,0,0.2)',
              borderRadius: '4px',
            }
          }}
        >
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px' }}>
              <CircularProgress />
            </Box>
          ) : filteredSchemes.length === 0 ? (
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center', 
              height: '200px',
              textAlign: 'center'
            }}>
              <Typography color="text.secondary">
                {t.noSchemesFound}
              </Typography>
            </Box>
          ) : (
            <Grid container spacing={3}>
              {filteredSchemes.map(scheme => (
                <Grid 
                  item 
                  xs={12} 
                  sm={6} 
                  md={4} 
                  lg={3} 
                  key={scheme.id}
                >
                  <SchemeCard scheme={scheme} onClick={handleSchemeClick} />
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      </Container>
    </Box>
  );
};

export default DiscoverPage; 