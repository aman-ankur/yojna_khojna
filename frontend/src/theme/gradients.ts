import { alpha } from '@mui/material/styles';

// Define base color constants
const DEEP_PURPLE = '#4A55A2';
const BLUE = '#7895CB';

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

// Pre-defined gradients for the sidebar
export const sidebarGradients = {
  // Default state gradient (deep purple to blue)
  default: createGradient({
    colors: [DEEP_PURPLE, BLUE],
    direction: 'to right'
  }),
  
  // Active state gradient (slightly brighter)
  active: createGradient({
    colors: [alpha(DEEP_PURPLE, 0.9), alpha(BLUE, 0.9)],
    direction: 'to right'
  }),
  
  // Hover state gradient
  hover: createGradient({
    colors: [alpha(DEEP_PURPLE, 0.8), alpha(BLUE, 0.8)],
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
      boxShadow: `0 4px 12px ${alpha(DEEP_PURPLE, 0.4)}`,
    };
  }
  
  if (variant === 'active') {
    return {
      ...baseStyles,
      boxShadow: `0 4px 20px ${alpha(DEEP_PURPLE, 0.5)}`,
      borderLeft: `3px solid ${alpha(BLUE, 0.9)}`,
    };
  }
  
  return baseStyles;
};

// Export color constants for reuse
export const gradientColors = {
  DEEP_PURPLE,
  BLUE,
}; 