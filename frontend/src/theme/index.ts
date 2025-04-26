import { ThemeOptions } from '@mui/material/styles';

// Define custom theme options for MUI
const themeOptions: ThemeOptions = {
  palette: {
    primary: {
      main: '#8667D0', // Purple accent color
    },
    secondary: {
      main: '#7254C6', // Darker purple for hover states
    },
    background: {
      default: '#FFFFFF', // White background
      paper: '#FFFFFF', // White for cards/paper elements
    },
    text: {
      primary: '#1A1A1A',
      secondary: 'rgba(0,0,0,0.6)',
    },
  },
  typography: {
    fontFamily: '"Noto Sans", "Noto Sans Devanagari", "Roboto", "Helvetica", "Arial", sans-serif',
    h3: {
      fontWeight: 500,
      fontSize: '2rem',
    },
    h4: {
      fontWeight: 500,
      fontSize: '1.5rem',
    },
    body1: {
      fontSize: '0.9rem',
    },
    body2: {
      fontSize: '0.85rem',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none', // Prevent uppercase buttons
          borderRadius: '20px',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: '8px',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: 'none',
        },
      },
    },
    MuiButtonBase: {
      styleOverrides: {
        root: {
          '&:focus-visible': {
            outline: '2px solid #8667D0',
            outlineOffset: '2px'
          }
        }
      }
    },
    MuiInputBase: {
      styleOverrides: {
        root: {
          '&:focus-within': {
            boxShadow: '0 0 0 2px #8667D0'
          }
        }
      }
    }
  },
};

export default themeOptions; 