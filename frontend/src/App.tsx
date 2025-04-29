import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import themeOptions from './theme';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Import the components and providers
import Sidebar from './components/Sidebar';
import ChatContainer from './components/ChatContainer';
import DiscoverPage from './components/schemes/DiscoverPage';
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
      <Router>
        <LanguageProvider>
          <ConversationProvider>
            <ErrorBoundary>
              {/* Root container with fixed height and no overflow */}
              <Box
                sx={{
                  display: 'flex',
                  height: '100vh',
                  width: '100vw',
                  overflow: 'hidden',
                  backgroundColor: 'background.default'
                }}
                data-testid="main-layout-box"
              >
                {/* Left sidebar for navigation */}
                <Sidebar sx={{ flexShrink: 0 }} />
                
                {/* Main content area */}
                <Box
                  component="main"
                  sx={{
                    flexGrow: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    height: '100%',
                    overflow: 'hidden',
                    position: 'relative'
                  }}
                >
                  {/* Routing for different pages */}
                  <Routes>
                    <Route path="/chat" element={<ChatContainer data-testid="chat-container-component" />} />
                    <Route path="/discover" element={<DiscoverPage />} />
                    <Route path="/" element={<Navigate to="/chat" replace />} />
                  </Routes>
                </Box>
              </Box>
            </ErrorBoundary>
          </ConversationProvider>
        </LanguageProvider>
      </Router>
    </ThemeProvider>
  );
}

export default App;
