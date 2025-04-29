import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import themeOptions from './theme';

// Import the components and providers
import Sidebar from './components/Sidebar';
import ChatContainer from './components/ChatContainer';
import { LanguageProvider } from './components/LanguageToggle';
import ErrorBoundary from './components/ErrorBoundary';

// Create context providers wrapper for conversation functionality
import ConversationProvider from './context/ConversationProvider';

// Create MUI theme instance
const theme = createTheme(themeOptions);

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {/* Root container with fixed height and no overflow */}
      <LanguageProvider>
        <ErrorBoundary>
          <ConversationProvider>
            {/* Main application layout */}
            <Box 
              data-testid="main-layout-box"
              sx={{ 
                display: 'flex', 
                height: '100vh',
                overflow: 'hidden',
                flexDirection: { xs: 'column', sm: 'row' },
                p: { xs: 1, sm: 2 },
                gap: 2,
                boxSizing: 'border-box',
              }}
            >
              {/* Sidebar with conversation history */}
              <Sidebar 
                sx={{ 
                  width: { xs: '100%', sm: '48px' },
                  height: { xs: '48px', sm: 'auto' },
                  flexDirection: { xs: 'row', sm: 'column' }
                }} 
              />
              
              {/* Main chat container with its own error boundary */}
              <ErrorBoundary>
                <Box
                  className="main-chat-wrapper"
                  sx={{
                    flex: 1,
                    height: { xs: 'calc(100vh - 80px)', sm: 'auto' },
                    display: 'flex',
                    flexDirection: 'column',
                    overflow: 'hidden',
                  }}
                >
                  <ChatContainer />
                </Box>
              </ErrorBoundary>
            </Box>
          </ConversationProvider>
        </ErrorBoundary>
      </LanguageProvider>
    </ThemeProvider>
  );
}

export default App;
