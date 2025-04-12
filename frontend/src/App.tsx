import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import themeOptions from './theme';

// Import the components
import Sidebar from './components/Sidebar';
import ChatContainer from './components/ChatContainer';
import { LanguageProvider } from './components/LanguageToggle';

// Create MUI theme instance
const theme = createTheme(themeOptions);

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {/* Global styles are now in index.css */}
      <LanguageProvider>
        {/* Main application layout */}
        <Box 
          data-testid="main-layout-box"
          sx={{ 
            display: 'flex', 
            height: '100vh',
            overflow: 'hidden',
            flexDirection: { xs: 'column', sm: 'row' },
            p: { xs: 1, sm: 2 },
            gap: 2
          }}
        >
          {/* Mobile-friendly sidebar */}
          <Sidebar 
            sx={{ 
              width: { xs: '100%', sm: '48px' },
              height: { xs: '48px', sm: 'auto' },
              flexDirection: { xs: 'row', sm: 'column' }
            }} 
          />
          
          {/* Main chat container - Remove hardcoded userName */}
          <ChatContainer />
        </Box>
      </LanguageProvider>
    </ThemeProvider>
  );
}

export default App;
