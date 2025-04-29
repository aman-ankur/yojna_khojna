import { FC, useState } from 'react';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import Drawer from '@mui/material/Drawer';
import Backdrop from '@mui/material/Backdrop';
import useMediaQuery from '@mui/material/useMediaQuery';
import { useTheme } from '@mui/material/styles';

// Components
import ConversationList from './ConversationList';

// Hooks
import useConversations from '../hooks/useConversations';
import useCurrentConversation from '../hooks/useCurrentConversation';

// Icons
import AppLogo from '../assets/ChatGPT Image Apr 12 2025 Logo Design Ideas (2).png';
import CloseIcon from '@mui/icons-material/Close';
import AddIcon from '@mui/icons-material/Add';
import ChatIcon from '@mui/icons-material/Chat';
import HomeIcon from '@mui/icons-material/Home';
import SettingsIcon from '@mui/icons-material/Settings';
import MenuIcon from '@mui/icons-material/Menu';
import { useLanguage } from './LanguageToggle';

// Sidebar width constants
const COLLAPSED_WIDTH = 48;
const EXPANDED_WIDTH = 280;

interface SidebarProps {
  sx?: Record<string, any>;
}

const Sidebar: FC<SidebarProps> = ({ sx = {} }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { t } = useLanguage();
  
  // State
  const [expanded, setExpanded] = useState(false);
  
  // Hooks for conversation management
  const { 
    conversations, 
    loading: conversationsLoading, 
    createConversation, 
    deleteConversation 
  } = useConversations();
  
  const { 
    currentConversation, 
    switchConversation,
    createNewConversation 
  } = useCurrentConversation();
  
  // Handlers
  const toggleExpanded = () => {
    setExpanded(!expanded);
  };
  
  const handleClose = () => {
    setExpanded(false);
  };
  
  const handleNewConversation = () => {
    if (isMobile) {
      // Create and close sidebar on mobile
      createNewConversation();
      setExpanded(false);
    } else {
      // Just create on desktop
      createNewConversation();
    }
  };
  
  const handleSelectConversation = (id: string) => {
    switchConversation(id);
    if (isMobile) {
      setExpanded(false);
    }
  };
  
  // The sidebar content - both collapsed and expanded views share this
  const sidebarContent = (
    <>
      {/* Collapsed sidebar view */}
      <Box
        sx={{
          width: COLLAPSED_WIDTH,
          backgroundColor: '#f7f7f7',
          borderRight: '1px solid rgba(0,0,0,0.08)',
          display: expanded && !isMobile ? 'none' : 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          padding: '12px 0',
          justifyContent: 'space-between',
          height: '100%',
          ...sx
        }}
      >
        <Stack spacing={2} alignItems="center">
          {/* Logo */}
          <Box
            component="img"
            src={AppLogo}
            alt="Yojna Khojna Logo"
            sx={{ 
              width: 32,
              height: 32,
              mb: 1
            }}
          />
          
          {/* Toggle expand button */}
          <Tooltip title={expanded ? t.collapse : t.expand} placement="right">
            <IconButton onClick={toggleExpanded} data-testid="toggle-sidebar">
              <MenuIcon />
            </IconButton>
          </Tooltip>
          
          {/* Quick actions */}
          <Tooltip title={t.newConversation} placement="right">
            <IconButton onClick={handleNewConversation} data-testid="new-chat-button">
              <AddIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title={t.conversations} placement="right">
            <IconButton onClick={toggleExpanded}>
              <ChatIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title={t.home} placement="right">
            <IconButton>
              <HomeIcon />
            </IconButton>
          </Tooltip>
        </Stack>
        
        {/* Settings at the bottom */}
        <Tooltip title={t.settings} placement="right">
          <IconButton>
            <SettingsIcon />
          </IconButton>
        </Tooltip>
      </Box>
    </>
  );

  // Mobile implementation uses a temporary drawer
  if (isMobile) {
    return (
      <>
        {/* Always show collapsed sidebar on mobile */}
        {sidebarContent}
        
        {/* Conversation drawer for mobile */}
        <Drawer
          anchor="left"
          open={expanded}
          onClose={handleClose}
          ModalProps={{
            keepMounted: true, // Better mobile performance
          }}
          sx={{
            '& .MuiDrawer-paper': {
              width: EXPANDED_WIDTH,
              boxSizing: 'border-box',
            },
          }}
        >
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              p: 2
            }}
          >
            <Box
              component="img"
              src={AppLogo}
              alt="Yojna Khojna Logo"
              sx={{ 
                width: 32,
                height: 32
              }}
            />
            
            <IconButton onClick={handleClose}>
              <CloseIcon />
            </IconButton>
          </Box>
          
          <ConversationList
            conversations={conversations}
            currentConversationId={currentConversation?.id || null}
            loading={conversationsLoading}
            onSelectConversation={handleSelectConversation}
            onDeleteConversation={deleteConversation}
            onNewConversation={handleNewConversation}
          />
        </Drawer>
        
        {/* Backdrop for mobile */}
        <Backdrop
          sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer - 1 }}
          open={expanded}
          onClick={handleClose}
        />
      </>
    );
  }

  // Desktop implementation uses side-by-side display
  return (
    <>
      {/* Always visible collapsed sidebar */}
      {sidebarContent}
      
      {/* Expanded sidebar for desktop */}
      {expanded && (
        <Box
          sx={{
            width: EXPANDED_WIDTH,
            backgroundColor: '#f7f7f7',
            borderRight: '1px solid rgba(0,0,0,0.08)',
            height: '100%',
            position: 'relative',
            zIndex: 1200,
          }}
          data-testid="expanded-sidebar"
        >
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              p: 2
            }}
          >
            <Box
              component="img"
              src={AppLogo}
              alt="Yojna Khojna Logo"
              sx={{ 
                width: 32,
                height: 32
              }}
            />
            
            <IconButton onClick={handleClose}>
              <CloseIcon />
            </IconButton>
          </Box>
          
          <ConversationList
            conversations={conversations}
            currentConversationId={currentConversation?.id || null}
            loading={conversationsLoading}
            onSelectConversation={handleSelectConversation}
            onDeleteConversation={deleteConversation}
            onNewConversation={handleNewConversation}
          />
        </Box>
      )}
    </>
  );
};

export default Sidebar; 