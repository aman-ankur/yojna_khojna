import { ThemeOptions } from '@mui/material/styles';
import { gradientColors } from './gradients';

// Define custom theme options for MUI
const themeOptions: ThemeOptions = {
  palette: {
    primary: {
      main: gradientColors.DEEP_PURPLE, // Updated to use our muted purple color
    },
    secondary: {
      main: gradientColors.LIGHTER_PURPLE, // Updated to use the softer lavender shade
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
            outline: `2px solid ${gradientColors.DEEP_PURPLE}`,
            outlineOffset: '2px'
          }
        }
      }
    },
    MuiInputBase: {
      styleOverrides: {
        root: {
          '&:focus-within': {
            boxShadow: `0 0 0 2px ${gradientColors.DEEP_PURPLE}`
          }
        }
      }
    },
    // Add new component styling for list items used in sidebar
    MuiListItem: {
      styleOverrides: {
        root: {
          borderRadius: '8px',
          margin: '4px 0',
          transition: 'all 0.2s ease-in-out',
        }
      }
    },
    // Style the IconButton component for sidebar
    MuiIconButton: {
      styleOverrides: {
        root: {
          transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
          '&:hover': {
            transform: 'translateY(-2px)',
          }
        }
      }
    },
    // Add tooltip styling for better visibility
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.85)',
          padding: '8px 12px',
          fontSize: '0.8rem',
        }
      }
    },
    // Update chip styling for category filters
    MuiChip: {
      styleOverrides: {
        root: {
          '&.MuiChip-filled': {
            backgroundColor: gradientColors.DEEP_PURPLE,
            color: '#fff',
          },
          '&.MuiChip-outlined': {
            borderColor: `rgba(${parseInt(gradientColors.DEEP_PURPLE.slice(1, 3), 16)}, ${parseInt(gradientColors.DEEP_PURPLE.slice(3, 5), 16)}, ${parseInt(gradientColors.DEEP_PURPLE.slice(5, 7), 16)}, 0.5)`,
            color: gradientColors.DEEP_PURPLE,
          }
        }
      }
    }
  },
};

export default themeOptions; 