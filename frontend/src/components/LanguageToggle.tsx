import { FC, createContext, useContext, useState, ReactNode } from 'react';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import Tooltip from '@mui/material/Tooltip';

// Define the language context type
interface LanguageContextType {
  language: 'hi' | 'en';
  toggleLanguage: () => void;
  t: Record<string, string>;
}

// Create the context with default values
const LanguageContext = createContext<LanguageContextType>({
  language: 'hi',
  toggleLanguage: () => {},
  t: {},
});

// Translations object
const translations = {
  hi: {
    welcome: 'नमस्ते',
    question: 'आप क्या जानना चाहेंगे?',
    subtitle: 'नीचे दिए गए सुझावों में से एक चुनें या अपना प्रश्न पूछें',
    inputPlaceholder: 'अपना प्रश्न यहां लिखें...',
    chatPlaceholder: 'आप क्या जानना चाहते हैं...',
    uploadImage: 'चित्र अपलोड करें',
    attachment: 'अटैचमेंट जोड़ें',
    uploading: 'चित्र अपलोड हो रहा है...',
    refreshSuggestions: 'सुझाव रीफ्रेश करें',
    eligibility: "योजना के लिए पात्रता की जांच करें",
    applicationProcess: "आवेदन प्रक्रिया के बारे में पूछें",
    benefits: "योजना के लाभों की जानकारी पाएं",
    govtHelp: "सरकारी सहायता के बारे में पूछें",
    error: 'कोई त्रुटि हुई। कृपया पुनः प्रयास करें।',
  },
  en: {
    welcome: 'Hello',
    question: 'What would you like to know?',
    subtitle: 'Choose one of the suggestions below or ask your own question',
    inputPlaceholder: 'Type your question here...',
    chatPlaceholder: 'What would you like to know...',
    uploadImage: 'Upload image',
    attachment: 'Add attachment',
    uploading: 'Uploading image...',
    refreshSuggestions: 'Refresh suggestions',
    eligibility: "Check eligibility for schemes",
    applicationProcess: "Ask about application process",
    benefits: "Get information about scheme benefits",
    govtHelp: "Ask about government assistance",
    error: 'An error occurred. Please try again.',
  }
};

// Language provider component
interface LanguageProviderProps {
  children: ReactNode;
}

export const LanguageProvider: FC<LanguageProviderProps> = ({ children }) => {
  const [language, setLanguage] = useState<'hi' | 'en'>('hi'); // Default to Hindi
  
  const toggleLanguage = () => {
    setLanguage(prev => prev === 'hi' ? 'en' : 'hi');
  };
  
  return (
    <LanguageContext.Provider value={{ 
      language, 
      toggleLanguage, 
      t: translations[language] 
    }}>
      {children}
    </LanguageContext.Provider>
  );
};

// Custom hook for using the language context
export const useLanguage = () => useContext(LanguageContext);

// Language toggle button component
const LanguageToggle: FC = () => {
  const { language, toggleLanguage } = useLanguage();
  
  return (
    <Tooltip title={language === 'hi' ? 'Switch to English' : 'हिंदी में बदलें'}>
      <IconButton 
        onClick={toggleLanguage}
        aria-label={language === 'hi' ? 'Switch to English' : 'Switch to Hindi'}
        sx={{
          border: '1px solid rgba(0,0,0,0.08)',
          borderRadius: '50%',
          width: 36,
          height: 36,
        }}
      >
        <Typography 
          variant="button" 
          sx={{ 
            fontWeight: 'bold',
            fontSize: '14px'
          }}
        >
          {language === 'hi' ? 'EN' : 'हि'}
        </Typography>
      </IconButton>
    </Tooltip>
  );
};

export default LanguageToggle; 