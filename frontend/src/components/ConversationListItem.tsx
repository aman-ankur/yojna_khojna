import { FC, useState } from 'react';
import { Conversation } from '../services/conversationService';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import { formatDistanceToNow } from 'date-fns';
import { useLanguage } from './LanguageToggle';

interface ConversationListItemProps {
  conversation: Conversation;
  isActive: boolean;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
  onRename?: (id: string, newTitle: string) => void;
}

const ConversationListItem: FC<ConversationListItemProps> = ({
  conversation,
  isActive,
  onSelect,
  onDelete,
  onRename
}) => {
  const { t } = useLanguage();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [newTitle, setNewTitle] = useState(conversation.title);
  
  // Format the date to relative time (e.g., "2 days ago")
  const formattedDate = formatDistanceToNow(new Date(conversation.updatedAt), { addSuffix: true });
  
  const handleSelect = () => {
    if (!isEditing) {
      onSelect(conversation.id);
    }
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

  const handleEditClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering the onSelect
    setIsEditing(true);
    setNewTitle(conversation.title);
  };

  const handleCancelEdit = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering the onSelect
    setIsEditing(false);
    setNewTitle(conversation.title);
  };

  const handleSaveEdit = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering the onSelect
    if (onRename && newTitle.trim() !== '') {
      onRename(conversation.id, newTitle.trim());
    }
    setIsEditing(false);
  };

  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNewTitle(e.target.value);
  };

  const handleTitleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && newTitle.trim() !== '') {
      if (onRename) {
        onRename(conversation.id, newTitle.trim());
      }
      setIsEditing(false);
    } else if (e.key === 'Escape') {
      setIsEditing(false);
      setNewTitle(conversation.title);
    }
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
          cursor: isEditing ? 'default' : 'pointer',
          backgroundColor: isActive ? '#f0f0f0' : 'transparent',
          '&:hover': {
            backgroundColor: isActive ? '#f0f0f0' : '#f7f7f7',
          }
        }}
        data-testid={`conversation-item-${conversation.id}`}
      >
        <Box sx={{ overflow: 'hidden', flex: 1 }}>
          {isEditing ? (
            <TextField
              fullWidth
              size="small"
              value={newTitle}
              onChange={handleTitleChange}
              onKeyDown={handleTitleKeyDown}
              autoFocus
              onClick={(e) => e.stopPropagation()}
              inputProps={{ 'data-testid': 'edit-conversation-title' }}
            />
          ) : (
            <>
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
            </>
          )}
        </Box>
        
        {isEditing ? (
          <Box sx={{ display: 'flex' }}>
            <IconButton 
              size="small" 
              onClick={handleSaveEdit}
              aria-label={t.save}
            >
              <CheckIcon fontSize="small" />
            </IconButton>
            <IconButton 
              size="small" 
              onClick={handleCancelEdit}
              aria-label={t.cancel}
            >
              <CloseIcon fontSize="small" />
            </IconButton>
          </Box>
        ) : (
          <Box sx={{ display: 'flex' }}>
            {onRename && (
              <IconButton 
                size="small" 
                onClick={handleEditClick}
                aria-label={t.renameConversation || "Rename"}
              >
                <EditIcon fontSize="small" />
              </IconButton>
            )}
            <IconButton 
              size="small" 
              onClick={handleDeleteClick}
              aria-label={t.deleteConversation}
            >
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Box>
        )}
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