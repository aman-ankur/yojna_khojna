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
    // New conversation history translations
    conversations: 'वार्तालाप',
    newConversation: 'नई वार्तालाप',
    deleteConversation: 'वार्तालाप हटाएं',
    deleteConversationTitle: 'वार्तालाप हटाएं?',
    deleteConversationConfirm: 'क्या आप इस वार्तालाप को हटाना चाहते हैं',
    cancel: 'रद्द करें',
    delete: 'हटाएं',
    noConversations: 'कोई वार्तालाप नहीं। नया बनाने के लिए ऊपर बटन पर क्लिक करें।',
    expand: 'विस्तार करें',
    collapse: 'संकुचित करें',
    home: 'होम',
    settings: 'सेटिंग्स',
    confirmDelete: 'हटाने की पुष्टि करें',
    maxConversationsReached: 'अधिकतम वार्तालाप सीमा (25) तक पहुंच गए हैं। जारी रखने के लिए किसी वार्तालाप को हटाएं।',
    pinnedConversations: "पिन किए गए",
    otherConversations: "अन्य वार्तालाप",
    pinConversation: "इस वार्तालाप को पिन करें",
    unpinConversation: "इस वार्तालाप को अनपिन करें",
    pinLimitReached: "पिन सीमा पहुँच गई (3)",
    pinLimitReachedTitle: "पिन सीमा पहुँच गई",
    pinLimitReachedMessage: "आप अधिकतम 3 वार्तालाप पिन कर सकते हैं। नया वार्तालाप पिन करने से पहले किसी मौजूदा वार्तालाप को अनपिन करें।",
    ok: "ठीक है",
    // Discover Page
    discover: "खोजें",
    discoverSchemes: "योजनाएँ खोजें",
    discoverSchemesDescription: "विभिन्न श्रेणियों में सरकारी योजनाओं का पता लगाएं। किसी भी योजना के बारे में बातचीत शुरू करने के लिए उस पर क्लिक करें।",
    searchSchemes: "योजनाएँ खोजें...",
    noSchemesFound: "आपके फ़िल्टर से मेल खाती कोई योजना नहीं मिली। अपनी खोज या श्रेणी चयन को समायोजित करने का प्रयास करें।",
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
    // New conversation history translations
    conversations: 'Conversations',
    newConversation: 'New Conversation',
    deleteConversation: 'Delete Conversation',
    deleteConversationTitle: 'Delete Conversation?',
    deleteConversationConfirm: 'Are you sure you want to delete the conversation',
    cancel: 'Cancel',
    delete: 'Delete',
    noConversations: 'No conversations yet. Click the button above to create one.',
    expand: 'Expand',
    collapse: 'Collapse',
    home: 'Home',
    settings: 'Settings',
    confirmDelete: 'Confirm Delete',
    maxConversationsReached: 'Maximum conversation limit (25) reached. Delete a conversation to continue.',
    pinnedConversations: "Pinned",
    otherConversations: "Other Conversations",
    pinConversation: "Pin this conversation",
    unpinConversation: "Unpin this conversation",
    pinLimitReached: "Pin limit reached (3)",
    pinLimitReachedTitle: "Pin Limit Reached",
    pinLimitReachedMessage: "You can pin a maximum of 3 conversations. Please unpin an existing conversation before pinning a new one.",
    ok: "OK",
    // Discover Page
    discover: "Discover",
    discoverSchemes: "Discover Schemes",
    discoverSchemesDescription: "Explore government schemes across different categories. Click on any scheme to start a conversation about it.",
    searchSchemes: "Search schemes...",
    noSchemesFound: "No schemes found matching your filters. Try adjusting your search or category selection.",
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