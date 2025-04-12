import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import './App.css'
import ChatInterface from './components/ChatInterface'
import themeOptions from './theme' // We'll create this next

// Create MUI theme instance
const theme = createTheme(themeOptions);

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ bgcolor: 'grey.50', minHeight: '100vh', py: 5 }}>
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', mb: 10 }}>
            <Typography variant="h3" component="h1" sx={{ mb: 2, color: 'primary.main' }}>
              Yojna Khojna
            </Typography>
            <Typography variant="h6" sx={{ color: 'text.secondary' }}>
              Ask questions about government schemes and get accurate answers
            </Typography>
          </Box>
          
          <ChatInterface />
        </Container>
      </Box>
    </ThemeProvider>
  )
}

export default App
