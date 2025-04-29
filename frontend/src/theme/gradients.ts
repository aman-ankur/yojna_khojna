import { alpha } from '@mui/material/styles';

// Define base color constants - Updated to match "नागरिक" purple branding with a muted, elegant tone
const DEEP_PURPLE = '#635089'; // Muted, darker purple
const LIGHTER_PURPLE = '#8A7AAD'; // Softer lavender shade
const ACCENT_PURPLE = '#6F5F9E'; // Slightly deeper for active states

// Define gradient types
export interface GradientOptions {
  colors: string[];
  direction?: string;
  opacity?: number;
}

// Utility function to create gradient string
export const createGradient = (options: GradientOptions): string => {
  const { colors, direction = '145deg', opacity = 1 } = options;
  
  // Apply opacity to all colors
  const gradientColors = colors.map(color => {
    if (opacity < 1) {
      return alpha(color, opacity);
    }
    return color;
  });
  
  return `linear-gradient(${direction}, ${gradientColors.join(', ')})`;
};

// Pre-defined gradients for the sidebar - Updated with new muted purple palette
export const sidebarGradients = {
  // Default state gradient (muted purple to softer lavender)
  default: createGradient({
    colors: [DEEP_PURPLE, LIGHTER_PURPLE],
    direction: 'to right',
    opacity: 0.95 // Slightly reduced opacity for subtlety
  }),
  
  // Active state gradient (slightly deeper with more contrast)
  active: createGradient({
    colors: [ACCENT_PURPLE, LIGHTER_PURPLE],
    direction: 'to right',
    opacity: 0.97 // Higher opacity for active state
  }),
  
  // Hover state gradient (subtle depth change)
  hover: createGradient({
    colors: [DEEP_PURPLE, alpha(LIGHTER_PURPLE, 0.85)],
    direction: 'to right'
  }),
};

// Create gradient styles for components
export const createGradientStyles = (variant: 'default' | 'active' | 'hover' = 'default') => {
  const baseStyles = {
    background: sidebarGradients[variant],
    color: '#FFFFFF', // White text for contrast
    transition: 'all 0.2s ease-in-out',
  };
  
  // Additional styles based on variant
  if (variant === 'hover') {
    return {
      ...baseStyles,
      boxShadow: `0 2px 8px ${alpha(DEEP_PURPLE, 0.3)}`, // More subtle shadow
    };
  }
  
  if (variant === 'active') {
    return {
      ...baseStyles,
      boxShadow: `0 2px 10px ${alpha(ACCENT_PURPLE, 0.4)}`, // Reduced shadow intensity
      borderLeft: `2px solid ${LIGHTER_PURPLE}`, // Thinner border
    };
  }
  
  return baseStyles;
};

// Export color constants for reuse
export const gradientColors = {
  DEEP_PURPLE,
  ACCENT_PURPLE,
  LIGHTER_PURPLE
}; 