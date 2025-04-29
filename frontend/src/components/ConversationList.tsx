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

interface ConversationListProps {
  conversations: Conversation[];
  currentConversationId: string | null;
  loading: boolean;
  onSelectConversation: (id: string) => void;
  onDeleteConversation: (id: string) => void;
  onRenameConversation?: (id: string, newTitle: string) => void;
  onNewConversation: () => void;
}

const ConversationList: FC<ConversationListProps> = ({
  conversations,
  currentConversationId,
  loading,
  onSelectConversation,
  onDeleteConversation,
  onRenameConversation,
  onNewConversation
}) => {
  const { t } = useLanguage();

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
        <Typography variant="h6" component="h2">
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
        ) : conversations.length === 0 ? (
          <Typography variant="body2" color="text.secondary" align="center" sx={{ pt: 4 }}>
            {t.noConversations}
          </Typography>
        ) : (
          conversations.map((conversation) => (
            <ConversationListItem
              key={conversation.id}
              conversation={conversation}
              isActive={conversation.id === currentConversationId}
              onSelect={onSelectConversation}
              onDelete={onDeleteConversation}
              onRename={onRenameConversation}
            />
          ))
        )}
      </Box>
    </Box>
  );
};

export default ConversationList; 