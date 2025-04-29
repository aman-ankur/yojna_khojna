import { FC } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Divider from '@mui/material/Divider';
import AddIcon from '@mui/icons-material/Add';
import ConversationListItem from './ConversationListItem';
import { Conversation } from '../services/conversationService';
import { useLanguage } from './LanguageToggle';
import CircularProgress from '@mui/material/CircularProgress';
import { sidebarGradients, gradientColors } from '../theme/gradients';
import PushPinIcon from '@mui/icons-material/PushPin';
import { alpha } from '@mui/material/styles';

interface ConversationListProps {
  conversations: Conversation[];
  pinnedConversations?: Conversation[];
  unpinnedConversations?: Conversation[];
  currentConversationId: string | null;
  loading: boolean;
  onSelectConversation: (id: string) => void;
  onDeleteConversation: (id: string) => void;
  onRenameConversation?: (id: string, newTitle: string) => void;
  onPinConversation?: (id: string) => void;
  onUnpinConversation?: (id: string) => void;
  onNewConversation: () => void;
  isPinLimitReached?: boolean;
}

const ConversationList: FC<ConversationListProps> = ({
  conversations,
  pinnedConversations = [],
  unpinnedConversations = [],
  currentConversationId,
  loading,
  onSelectConversation,
  onDeleteConversation,
  onRenameConversation,
  onPinConversation,
  onUnpinConversation,
  onNewConversation,
  isPinLimitReached = false
}) => {
  const { t } = useLanguage();
  const hasPinnedConversations = pinnedConversations.length > 0;
  const hasUnpinnedConversations = unpinnedConversations.length > 0;
  const shouldShowAllConversations = !hasPinnedConversations && !hasUnpinnedConversations;

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        width: '100%',
        overflow: 'hidden',
      }}
      data-testid="conversation-list"
    >
      {/* Header with new conversation button - fixed */}
      <Box
        sx={{
          p: 2,
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
          flexShrink: 0,
        }}
      >
        <Typography 
          variant="h6" 
          component="h2"
          sx={{
            background: sidebarGradients.default,
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text', 
            color: 'transparent',
            fontWeight: 600,
            opacity: 0.95
          }}
        >
          {t.conversations}
        </Typography>
        
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          fullWidth
          onClick={(e) => {
            console.log("ConversationList new conversation button clicked");
            onNewConversation();
          }}
          disabled={loading}
          data-testid="new-conversation-button"
          sx={{
            background: sidebarGradients.default,
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.12)',
            '&:hover': {
              background: sidebarGradients.hover,
            }
          }}
        >
          {t.newConversation}
        </Button>
      </Box>
      
      <Divider />
      
      {/* Conversation list - scrollable */}
      <Box
        className="conversations-scrollable"
        sx={{
          flex: 1,
          overflowY: 'auto',
          overflowX: 'hidden',
          p: 2,
          pt: 1,
          height: 0, // This forces flex to calculate the height correctly
          minHeight: 0,
        }}
      >
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', pt: 4 }}>
            <CircularProgress size={24} />
          </Box>
        ) : conversations.length === 0 && !hasPinnedConversations && !hasUnpinnedConversations ? (
          <Typography variant="body2" color="text.secondary" align="center" sx={{ pt: 4 }}>
            {t.noConversations}
          </Typography>
        ) : (
          <>
            {/* Pinned conversations section */}
            {hasPinnedConversations && (
              <Box sx={{ mb: 2 }}>
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  mb: 1,
                  px: 1
                }}>
                  <PushPinIcon 
                    fontSize="small" 
                    sx={{ 
                      color: alpha(gradientColors.ACCENT_PURPLE, 0.7),
                      fontSize: '0.9rem',
                      mr: 0.5,
                      transform: 'rotate(45deg)'
                    }} 
                  />
                  <Typography 
                    variant="caption" 
                    sx={{ 
                      fontWeight: 600,
                      color: 'text.secondary',
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px'
                    }}
                  >
                    {t.pinnedConversations || "Pinned"}
                  </Typography>
                </Box>
                
                {pinnedConversations.map((conversation) => (
                  <ConversationListItem
                    key={conversation.id}
                    conversation={conversation}
                    isActive={conversation.id === currentConversationId}
                    onSelect={onSelectConversation}
                    onDelete={onDeleteConversation}
                    onRename={onRenameConversation}
                    onPin={onPinConversation}
                    onUnpin={onUnpinConversation}
                    isPinned={true}
                    pinLimitReached={isPinLimitReached}
                  />
                ))}
              </Box>
            )}
            
            {/* Show divider between pinned and unpinned sections if both exist */}
            {hasPinnedConversations && hasUnpinnedConversations && (
              <Divider sx={{ my: 2 }} />
            )}
            
            {/* Other conversations section */}
            {hasUnpinnedConversations && (
              <Box>
                {hasPinnedConversations && (
                  <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    mb: 1,
                    px: 1
                  }}>
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        fontWeight: 600,
                        color: 'text.secondary',
                        textTransform: 'uppercase',
                        letterSpacing: '0.5px'
                      }}
                    >
                      {t.otherConversations || "Other Conversations"}
                    </Typography>
                  </Box>
                )}
                
                {unpinnedConversations.map((conversation) => (
                  <ConversationListItem
                    key={conversation.id}
                    conversation={conversation}
                    isActive={conversation.id === currentConversationId}
                    onSelect={onSelectConversation}
                    onDelete={onDeleteConversation}
                    onRename={onRenameConversation}
                    onPin={onPinConversation}
                    onUnpin={onUnpinConversation}
                    isPinned={false}
                    pinLimitReached={isPinLimitReached}
                  />
                ))}
              </Box>
            )}
            
            {/* Fall back to showing all conversations if pinned/unpinned are not provided */}
            {shouldShowAllConversations && (
              conversations.map((conversation) => (
                <ConversationListItem
                  key={conversation.id}
                  conversation={conversation}
                  isActive={conversation.id === currentConversationId}
                  onSelect={onSelectConversation}
                  onDelete={onDeleteConversation}
                  onRename={onRenameConversation}
                  onPin={onPinConversation}
                  onUnpin={onUnpinConversation}
                  isPinned={conversation.isPinned}
                  pinLimitReached={isPinLimitReached}
                />
              ))
            )}
          </>
        )}
      </Box>
    </Box>
  );
};

export default ConversationList; 