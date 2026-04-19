import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import DarkModeIcon from "@mui/icons-material/DarkMode";
import LightModeIcon from "@mui/icons-material/LightMode";
import NotificationsNoneIcon from "@mui/icons-material/NotificationsNone";
import SearchIcon from "@mui/icons-material/Search";
import {
  AppBar,
  Box,
  IconButton,
  InputBase,
  Stack,
  Toolbar,
  Tooltip,
  Typography,
  alpha,
} from "@mui/material";


import { OrgSwitcher } from "@/pages/shell/OrgSwitcher";
import { ProjectSwitcher } from "@/pages/shell/ProjectSwitcher";
import { useColorMode } from "@/theme";

export function TopBar() {
  const { mode, toggleMode } = useColorMode();
  const themeLabel = mode === "dark" ? "Switch to light mode" : "Switch to dark mode";

  return (
    <AppBar
      position="fixed"
      color="transparent"
      elevation={0}
      sx={{
        backdropFilter: "blur(8px)",
        borderBottom: 1,
        borderColor: "divider",
        backgroundColor: (t) => alpha(t.palette.background.default, 0.8),
        zIndex: (t) => t.zIndex.drawer + 1,
      }}
    >
      <Toolbar variant="dense" sx={{ gap: 1.5 }}>
        <Typography variant="subtitle1" fontWeight={700} sx={{ mr: 2 }}>
          MoveMind
        </Typography>
        <OrgSwitcher />
        <Typography color="text.disabled" aria-hidden="true">
          /
        </Typography>
        <ProjectSwitcher />
        <Box sx={{ flexGrow: 1 }} />
        <Box
          sx={{
            display: { xs: "none", md: "flex" },
            alignItems: "center",
            gap: 0.5,
            px: 1,
            py: 0.25,
            border: 1,
            borderColor: "divider",
            borderRadius: 1,
            width: 240,
            color: "text.secondary",
          }}
        >
          <SearchIcon fontSize="small" />
          <InputBase
            placeholder="Search (⌘K)"
            inputProps={{ "aria-label": "Search" }}
            sx={{ flex: 1, fontSize: 14 }}
          />
        </Box>
        <Stack direction="row" spacing={0.5}>
          <Tooltip title={themeLabel}>
            <IconButton aria-label={themeLabel} onClick={toggleMode} size="small">
              {mode === "dark" ? (
                <LightModeIcon fontSize="small" />
              ) : (
                <DarkModeIcon fontSize="small" />
              )}
            </IconButton>
          </Tooltip>
          <IconButton aria-label="Notifications" size="small">
            <NotificationsNoneIcon fontSize="small" />
          </IconButton>
          <IconButton aria-label="Account" size="small">
            <AccountCircleIcon fontSize="small" />
          </IconButton>
        </Stack>
      </Toolbar>
    </AppBar>
  );
}
