import { FC } from 'react';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import IconButton from '@mui/material/IconButton';
import Avatar from '@mui/material/Avatar';
import Tooltip from '@mui/material/Tooltip';

// Import the logo
import AppLogo from '../assets/ChatGPT Image Apr 12 2025 Logo Design Ideas (2).png';

// Icons
import CloseIcon from '@mui/icons-material/Close';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import HomeIcon from '@mui/icons-material/Home';
import FolderIcon from '@mui/icons-material/Folder';
import SettingsIcon from '@mui/icons-material/Settings';

interface SidebarProps {
  sx?: Record<string, any>;
}

const Sidebar: FC<SidebarProps> = ({ sx = {} }) => {
  return (
    <Box
      sx={{
        width: '48px',
        backgroundColor: '#f7f7f7',
        borderRight: '1px solid rgba(0,0,0,0.08)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: '12px 0',
        justifyContent: 'space-between',
        ...sx
      }}
    >
      <Stack spacing={2} alignItems="center">
        {/* Logo at the top */}
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
        
        {/* Top section with main navigation icons */}
        <Tooltip title="Close" placement="right">
          <IconButton><CloseIcon /></IconButton>
        </Tooltip>
        <Tooltip title="New Chat" placement="right">
          <IconButton><AddIcon /></IconButton>
        </Tooltip>
        <Tooltip title="Search" placement="right">
          <IconButton><SearchIcon /></IconButton>
        </Tooltip>
        <Tooltip title="Home" placement="right">
          <IconButton><HomeIcon /></IconButton>
        </Tooltip>
        <Tooltip title="Folders" placement="right">
          <IconButton><FolderIcon /></IconButton>
        </Tooltip>
      </Stack>
      
      {/* User avatar at bottom */}
      <Tooltip title="Settings" placement="right">
        <IconButton><SettingsIcon /></IconButton>
      </Tooltip>
    </Box>
  );
};

export default Sidebar; 