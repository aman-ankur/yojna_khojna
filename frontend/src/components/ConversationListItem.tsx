import { FC, useState } from 'react';
import { Conversation } from '../services/conversationService';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import PushPinIcon from '@mui/icons-material/PushPin';
import PushPinOutlinedIcon from '@mui/icons-material/PushPinOutlined';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Tooltip from '@mui/material/Tooltip';
import { formatDistanceToNow } from 'date-fns';
import { useLanguage } from './LanguageToggle';
import { createGradientStyles, sidebarGradients, gradientColors } from '../theme/gradients';
import { alpha } from '@mui/material/styles';

interface ConversationListItemProps {
  conversation: Conversation;
  isActive: boolean;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
  onRename?: (id: string, newTitle: string) => void;
  onPin?: (id: string) => void;
  onUnpin?: (id: string) => void;
  isPinned?: boolean;
  pinLimitReached?: boolean;
}

const ConversationListItem: FC<ConversationListItemProps> = ({
  conversation,
  isActive,
  onSelect,
  onDelete,
  onRename,
  onPin,
  onUnpin,
  isPinned = false,
  pinLimitReached = false
}) => {
  const { t } = useLanguage();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [pinLimitDialogOpen, setPinLimitDialogOpen] = useState(false);
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
  
  const handlePinClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering the onSelect
    if (!onPin) return;
    
    // Check if we're at the pin limit
    if (!isPinned && pinLimitReached) {
      setPinLimitDialogOpen(true);
      return;
    }
    
    try {
      onPin(conversation.id);
    } catch (error) {
      // Handle error (should be caught at the hook level)
      setPinLimitDialogOpen(true);
    }
  };
  
  const handleUnpinClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering the onSelect
    if (onUnpin) {
      onUnpin(conversation.id);
    }
  };
  
  const handlePinLimitClose = () => {
    setPinLimitDialogOpen(false);
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
  
  const isActionable = !isEditing;
  
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
          backgroundColor: isActive ? 
            sidebarGradients.active : 
            'transparent',
          backgroundImage: isActive ? sidebarGradients.active : 'none',
          color: isActive ? '#fff' : 'inherit',
          transition: 'all 0.2s ease-in-out',
          boxShadow: isActive ? 
            `0 2px 8px ${alpha(gradientColors.DEEP_PURPLE, 0.25)}` : 
            'none',
          borderLeft: isActive ? 
            `2px solid ${gradientColors.LIGHTER_PURPLE}` : 
            isPinned ? `1px solid ${alpha(gradientColors.DEEP_PURPLE, 0.3)}` :
            '1px solid transparent',
          '&:hover': {
            backgroundColor: !isActive && !isEditing ? 
              alpha(gradientColors.DEEP_PURPLE, 0.08) : 
              isActive ? sidebarGradients.active : 'transparent',
            boxShadow: !isActive && !isEditing ? 
              `0 1px 3px ${alpha(gradientColors.DEEP_PURPLE, 0.15)}` :
              isActive ? `0 2px 8px ${alpha(gradientColors.DEEP_PURPLE, 0.25)}` : 
              'none',
          }
        }}
        data-testid={`conversation-item-${conversation.id}`}
      >
        <Box sx={{ 
          overflow: 'hidden', 
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          ml: isPinned ? 0 : 0 // Keep alignment consistent whether pinned or not
        }}>
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
              sx={{
                '& .MuiOutlinedInput-root': {
                  '&.Mui-focused fieldset': {
                    borderColor: gradientColors.DEEP_PURPLE,
                  },
                },
              }}
            />
          ) : (
            <>
              <Typography
                variant="subtitle1"
                noWrap
                sx={{
                  fontWeight: isActive ? 'bold' : isPinned ? 'bold' : 'normal',
                  color: isActive ? '#fff' : 'inherit',
                  display: 'flex',
                  alignItems: 'center'
                }}
              >
                {isPinned && (
                  <PushPinIcon 
                    fontSize="small" 
                    sx={{ 
                      mr: 0.5, 
                      color: isActive ? '#fff' : alpha(gradientColors.ACCENT_PURPLE, 0.7),
                      transform: 'rotate(45deg)',
                      fontSize: '0.9rem' 
                    }} 
                  />
                )}
                {conversation.title}
              </Typography>
              <Typography 
                variant="caption" 
                noWrap
                sx={{ 
                  color: isActive ? alpha('#fff', 0.8) : 'text.secondary'
                }}
              >
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
              sx={{
                color: isActive ? '#fff' : gradientColors.DEEP_PURPLE,
              }}
            >
              <CheckIcon fontSize="small" />
            </IconButton>
            <IconButton 
              size="small" 
              onClick={handleCancelEdit}
              aria-label={t.cancel}
              sx={{
                color: isActive ? '#fff' : 'text.secondary',
              }}
            >
              <CloseIcon fontSize="small" />
            </IconButton>
          </Box>
        ) : (
          <Box sx={{ display: 'flex' }}>
            {/* Pin/Unpin Button */}
            {(onPin || onUnpin) && isActionable && (
              isPinned ? (
                <Tooltip title={t.unpinConversation || "Unpin"}>
                  <IconButton 
                    size="small" 
                    onClick={handleUnpinClick}
                    aria-label={t.unpinConversation || "Unpin"}
                    sx={{
                      color: isActive ? '#fff' : gradientColors.DEEP_PURPLE,
                      '&:hover': {
                        color: isActive ? alpha('#fff', 0.8) : alpha(gradientColors.DEEP_PURPLE, 0.8),
                      }
                    }}
                  >
                    <PushPinIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              ) : (
                <Tooltip title={
                  pinLimitReached ? 
                    (t.pinLimitReached || "Pin limit reached (3)") : 
                    (t.pinConversation || "Pin")
                }>
                  <IconButton 
                    size="small" 
                    onClick={handlePinClick}
                    aria-label={t.pinConversation || "Pin"}
                    sx={{
                      color: isActive ? '#fff' : 'text.secondary',
                      opacity: pinLimitReached ? 0.5 : 1,
                      '&:hover': {
                        color: isActive ? 
                          '#fff' : 
                          pinLimitReached ? 
                            'text.secondary' : 
                            gradientColors.ACCENT_PURPLE,
                      }
                    }}
                  >
                    <PushPinOutlinedIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              )
            )}
            
            {/* Edit Button */}
            {onRename && isActionable && (
              <IconButton 
                size="small" 
                onClick={handleEditClick}
                aria-label={t.renameConversation || "Rename"}
                sx={{
                  color: isActive ? '#fff' : 'text.secondary',
                  '&:hover': {
                    color: isActive ? '#fff' : gradientColors.DEEP_PURPLE,
                  }
                }}
              >
                <EditIcon fontSize="small" />
              </IconButton>
            )}
            
            {/* Delete Button */}
            <IconButton 
              size="small" 
              onClick={handleDeleteClick}
              aria-label={t.deleteConversation}
              sx={{
                color: isActive ? '#fff' : 'text.secondary',
                '&:hover': {
                  color: isActive ? '#fff' : '#d32f2f',
                }
              }}
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
          <Button 
            onClick={handleDeleteConfirm} 
            color="error" 
            autoFocus
            sx={{
              background: 'linear-gradient(to right, #d32f2f, #f44336)',
              color: '#fff',
              '&:hover': {
                background: 'linear-gradient(to right, #b71c1c, #d32f2f)',
              }
            }}
          >
            {t.delete}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Pin limit reached dialog */}
      <Dialog
        open={pinLimitDialogOpen}
        onClose={handlePinLimitClose}
        aria-labelledby="pin-limit-dialog-title"
        aria-describedby="pin-limit-dialog-description"
      >
        <DialogTitle id="pin-limit-dialog-title">
          {t.pinLimitReachedTitle || "Pin Limit Reached"}
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="pin-limit-dialog-description">
            {t.pinLimitReachedMessage || "You can pin a maximum of 3 conversations. Please unpin an existing conversation before pinning a new one."}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={handlePinLimitClose} 
            color="primary"
            autoFocus
            sx={{
              background: sidebarGradients.default,
              color: '#fff',
              '&:hover': {
                background: sidebarGradients.hover,
              }
            }}
          >
            {t.ok || "OK"}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default ConversationListItem; 