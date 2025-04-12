import { ThemeOptions } from '@mui/material/styles';
import { blue, grey } from '@mui/material/colors';

// Define custom theme options for MUI
const themeOptions: ThemeOptions = {
  palette: {
    primary: {
      main: blue[700], // Primary color (similar to brand.500/brand.700)
    },
    secondary: {
      main: grey[500],
    },
    background: {
      default: grey[50],
      paper: '#ffffff',
    },
    text: {
      primary: grey[900],
      secondary: grey[600],
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h3: {
      fontWeight: 700,
    },
    h6: {
      fontWeight: 400,
    },
    // Customize other variants as needed
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none', // Prevent uppercase buttons
          borderRadius: 8,
        },
      },
      variants: [
        {
          props: { variant: 'contained' },
          style: {
            boxShadow: 'none',
            '&:hover': {
              boxShadow: 'none',
            },
          },
        },
      ],
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.05)', // Subtle shadow
        },
      },
    },
  },
};

export default themeOptions; 