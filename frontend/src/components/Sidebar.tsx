import { FC, useState } from 'react';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import Drawer from '@mui/material/Drawer';
import Backdrop from '@mui/material/Backdrop';
import useMediaQuery from '@mui/material/useMediaQuery';
import { useTheme, alpha } from '@mui/material/styles';
import { useNavigate, useLocation } from 'react-router-dom';

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
import ExploreIcon from '@mui/icons-material/Explore';
import { useLanguage } from './LanguageToggle';

// Gradient styling
import { sidebarGradients, createGradientStyles, gradientColors } from '../theme/gradients';

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
  const navigate = useNavigate();
  const location = useLocation();
  
  // State
  const [expanded, setExpanded] = useState(false);
  
  // Hooks for conversation management
  const { 
    conversations, 
    pinnedConversations,
    unpinnedConversations,
    loading: conversationsLoading, 
    createConversation, 
    deleteConversation,
    renameConversation,
    pinConversation,
    unpinConversation,
    refreshConversations,
    isPinLimitReached
  } = useConversations();
  
  const { 
    currentConversation, 
    switchConversation,
    createNewConversation,
    refreshCurrentConversation
  } = useCurrentConversation();
  
  // Handlers
  const toggleExpanded = () => {
    setExpanded(!expanded);
  };
  
  const handleClose = () => {
    setExpanded(false);
  };
  
  const handleNewConversation = () => {
    console.log("New conversation button clicked"); // Debug log
    
    // Get the current conversation ID for comparison
    const previousConvId = currentConversation?.id;
    console.log("Previous conversation ID:", previousConvId);
    
    // Create the new conversation - this is all we need
    // It will automatically update the current conversation
    const newConv = createNewConversation();
    console.log("Created new conversation:", newConv); // Debug log
    
    // Navigate to chat page when creating new conversation
    navigate('/chat');
    
    if (isMobile) {
      // Close sidebar on mobile
      setExpanded(false);
    }
    
    // No need for additional refreshes - the event system will handle it
  };
  
  // Find or create a new conversation
  const findOrCreateNewConversation = () => {
    // Check if there's an existing empty conversation
    const emptyConversation = conversations.find(
      (c) => c.messages.length === 0 || (c.messages.length === 1 && c.messages[0].content === '')
    );
    
    if (emptyConversation) {
      // Use the existing empty conversation
      console.log("Using existing empty conversation:", emptyConversation.id);
      switchConversation(emptyConversation.id);
    } else {
      // Create a new conversation
      console.log("No empty conversation found, creating new one");
      createNewConversation();
    }
    
    // Navigate to chat page
    navigate('/chat');
    
    if (isMobile) {
      setExpanded(false);
    }
  };
  
  const handleSelectConversation = (id: string) => {
    switchConversation(id);
    // Navigate to chat page when selecting a conversation
    navigate('/chat');
    if (isMobile) {
      setExpanded(false);
    }
  };

  const handleNavigate = (path: string) => {
    navigate(path);
    if (isMobile) {
      setExpanded(false);
    }
  };
  
  // Additional handler for opening conversations sidebar
  const handleOpenConversationsList = () => {
    // Navigate to chat page
    navigate('/chat');
    // Expand the sidebar to show conversations
    setExpanded(true);
  };
  
  // Gradient styles for buttons
  const gradientButtonStyle = {
    background: sidebarGradients.default,
    borderRadius: '50%',
    color: '#fff',
    '&:hover': {
      background: sidebarGradients.hover,
      boxShadow: `0 2px 8px ${alpha(gradientColors.DEEP_PURPLE, 0.3)}`,
    },
    '&.active': {
      background: sidebarGradients.active,
      boxShadow: `0 2px 10px ${alpha(gradientColors.ACCENT_PURPLE, 0.4)}`,
    }
  };
  
  // Check if a path is active to apply active styles
  const isPathActive = (path: string) => {
    return location.pathname === path;
  };
  
  // The sidebar content - both collapsed and expanded views share this
  const sidebarContent = (
    <>
      {/* Collapsed sidebar view */}
      <Box
        sx={{
          width: COLLAPSED_WIDTH,
          backgroundColor: theme.palette.background.paper,
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
            <IconButton 
              onClick={toggleExpanded} 
              data-testid="toggle-sidebar"
              sx={gradientButtonStyle}
            >
              <MenuIcon />
            </IconButton>
          </Tooltip>
          
          {/* Quick actions */}
          <Tooltip title={t.newConversation} placement="right">
            <IconButton 
              onClick={(e) => {
                console.log("Sidebar add button clicked");
                handleNewConversation();
              }} 
              data-testid="new-chat-button"
              sx={{
                ...gradientButtonStyle,
                ...(isPathActive('/chat') && { 
                  background: sidebarGradients.active,
                  boxShadow: `0 2px 10px ${alpha(gradientColors.ACCENT_PURPLE, 0.4)}`,
                })
              }}
            >
              <AddIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title={t.conversations} placement="right">
            <IconButton 
              onClick={handleOpenConversationsList}
              sx={{
                ...gradientButtonStyle,
                ...(isPathActive('/chat') && { 
                  background: sidebarGradients.active,
                  boxShadow: `0 2px 10px ${alpha(gradientColors.ACCENT_PURPLE, 0.4)}`,
                })
              }}
            >
              <ChatIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title={t.discover || "Discover"} placement="right">
            <IconButton
              onClick={() => handleNavigate('/discover')}
              sx={{
                ...gradientButtonStyle,
                ...(isPathActive('/discover') && { 
                  background: sidebarGradients.active,
                  boxShadow: `0 2px 10px ${alpha(gradientColors.ACCENT_PURPLE, 0.4)}`,
                })
              }}
            >
              <ExploreIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title={t.home} placement="right">
            <IconButton
              onClick={findOrCreateNewConversation}
              sx={{
                ...gradientButtonStyle,
                ...(isPathActive('/') && { 
                  background: sidebarGradients.active,
                  boxShadow: `0 2px 10px ${alpha(gradientColors.ACCENT_PURPLE, 0.4)}`,
                })
              }}
            >
              <HomeIcon />
            </IconButton>
          </Tooltip>
        </Stack>
        
        {/* Settings at the bottom */}
        <Tooltip title={t.settings} placement="right">
          <IconButton
            sx={gradientButtonStyle}
          >
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
            pinnedConversations={pinnedConversations}
            unpinnedConversations={unpinnedConversations}
            currentConversationId={currentConversation?.id || null}
            loading={conversationsLoading}
            onSelectConversation={handleSelectConversation}
            onDeleteConversation={deleteConversation}
            onRenameConversation={renameConversation}
            onPinConversation={pinConversation}
            onUnpinConversation={unpinConversation}
            onNewConversation={handleNewConversation}
            isPinLimitReached={isPinLimitReached()}
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
            backgroundColor: theme.palette.background.paper,
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
            pinnedConversations={pinnedConversations}
            unpinnedConversations={unpinnedConversations}
            currentConversationId={currentConversation?.id || null}
            loading={conversationsLoading}
            onSelectConversation={handleSelectConversation}
            onDeleteConversation={deleteConversation}
            onRenameConversation={renameConversation}
            onPinConversation={pinConversation}
            onUnpinConversation={unpinConversation}
            onNewConversation={handleNewConversation}
            isPinLimitReached={isPinLimitReached()}
          />
        </Box>
      )}
    </>
  );
};

export default Sidebar; 