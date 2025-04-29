import { FC, useState } from 'react';
import { Conversation } from '../services/conversationService';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import DeleteIcon from '@mui/icons-material/Delete';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Button from '@mui/material/Button';
import { formatDistanceToNow } from 'date-fns';
import { useLanguage } from './LanguageToggle';

interface ConversationListItemProps {
  conversation: Conversation;
  isActive: boolean;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
}

const ConversationListItem: FC<ConversationListItemProps> = ({
  conversation,
  isActive,
  onSelect,
  onDelete
}) => {
  const { t } = useLanguage();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  
  // Format the date to relative time (e.g., "2 days ago")
  const formattedDate = formatDistanceToNow(new Date(conversation.updatedAt), { addSuffix: true });
  
  const handleSelect = () => {
    onSelect(conversation.id);
  };
  
  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering the onSelect
    setDeleteDialogOpen(true);
  };
  
  const handleDeleteConfirm = () => {
    onDelete(conversation.id);
    setDeleteDialogOpen(false);
  };
  
  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
  };
  
  return (
    <>
      <Box 
        onClick={handleSelect}
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          p: 2,
          mb: 1,
          borderRadius: 1,
          cursor: 'pointer',
          backgroundColor: isActive ? '#f0f0f0' : 'transparent',
          '&:hover': {
            backgroundColor: isActive ? '#f0f0f0' : '#f7f7f7',
          }
        }}
        data-testid={`conversation-item-${conversation.id}`}
      >
        <Box sx={{ overflow: 'hidden', flex: 1 }}>
          <Typography
            variant="subtitle1"
            noWrap
            sx={{
              fontWeight: isActive ? 'bold' : 'normal',
            }}
          >
            {conversation.title}
          </Typography>
          <Typography variant="caption" color="text.secondary" noWrap>
            {formattedDate}
          </Typography>
        </Box>
        
        <IconButton 
          size="small" 
          onClick={handleDeleteClick}
          aria-label={t.deleteConversation}
        >
          <DeleteIcon fontSize="small" />
        </IconButton>
      </Box>
      
      {/* Delete confirmation dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
        aria-labelledby="delete-dialog-title"
        aria-describedby="delete-dialog-description"
      >
        <DialogTitle id="delete-dialog-title">
          {t.deleteConversationTitle}
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="delete-dialog-description">
            {t.deleteConversationConfirm}: "{conversation.title}"
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel} color="primary">
            {t.cancel}
          </Button>
          <Button onClick={handleDeleteConfirm} color="error" autoFocus>
            {t.delete}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default ConversationListItem; 