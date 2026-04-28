import { type ReactElement } from "react";

import AccountTreeIcon from "@mui/icons-material/AccountTree";
import AssessmentIcon from "@mui/icons-material/Assessment";
import ChatIcon from "@mui/icons-material/Chat";
import DashboardIcon from "@mui/icons-material/Dashboard";
import ExtensionIcon from "@mui/icons-material/Extension";
import HistoryIcon from "@mui/icons-material/History";
import HomeIcon from "@mui/icons-material/Home";
import ReceiptIcon from "@mui/icons-material/Receipt";
import SettingsIcon from "@mui/icons-material/Settings";
import StorageIcon from "@mui/icons-material/Storage";
import {
  Box,
  Divider,
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
} from "@mui/material";
import { NavLink, useParams } from "react-router-dom";

const DRAWER_WIDTH = 232;

interface NavEntry {
  label: string;
  icon: ReactElement;
  to: (orgSlug: string, projectSlug: string | undefined) => string;
  scope: "org" | "project";
  disabled?: (projectSlug: string | undefined) => boolean;
}

const entries: NavEntry[] = [
  {
    label: "Dashboard",
    icon: <HomeIcon fontSize="small" />,
    to: (o) => `/orgs/${o}/dashboard`,
    scope: "org",
  },
  {
    label: "Overview",
    icon: <DashboardIcon fontSize="small" />,
    to: (o, p) => `/orgs/${o}/projects/${p ?? ""}/overview`,
    scope: "project",
    disabled: (p) => !p,
  },
  {
    label: "Investigate",
    icon: <ChatIcon fontSize="small" />,
    to: (o, p) => `/orgs/${o}/projects/${p ?? ""}/investigate`,
    scope: "project",
    disabled: (p) => !p,
  },
  {
    label: "Conversations",
    icon: <HistoryIcon fontSize="small" />,
    to: (o, p) => `/orgs/${o}/projects/${p ?? ""}/conversations`,
    scope: "project",
    disabled: (p) => !p,
  },
  {
    label: "Logs",
    icon: <StorageIcon fontSize="small" />,
    to: (o, p) => `/orgs/${o}/projects/${p ?? ""}/logs/connectors`,
    scope: "project",
    disabled: (p) => !p,
  },
  {
    label: "Integrations",
    icon: <ExtensionIcon fontSize="small" />,
    to: (o, p) => `/orgs/${o}/projects/${p ?? ""}/integrations/jira`,
    scope: "project",
    disabled: (p) => !p,
  },
  {
    label: "Code Context",
    icon: <AccountTreeIcon fontSize="small" />,
    to: (o, p) => `/orgs/${o}/projects/${p ?? ""}/code-context/mcp`,
    scope: "project",
    disabled: (p) => !p,
  },
  {
    label: "Evaluations",
    icon: <AssessmentIcon fontSize="small" />,
    to: (o, p) => `/orgs/${o}/projects/${p ?? ""}/evaluations`,
    scope: "project",
    disabled: (p) => !p,
  },
  {
    label: "Settings",
    icon: <SettingsIcon fontSize="small" />,
    to: (o, p) => `/orgs/${o}/projects/${p ?? ""}/settings`,
    scope: "project",
    disabled: (p) => !p,
  },
  {
    label: "Billing",
    icon: <ReceiptIcon fontSize="small" />,
    to: (o) => `/orgs/${o}/billing`,
    scope: "org",
  },
];

export { DRAWER_WIDTH };

export function LeftRail() {
  const { orgSlug, projectSlug } = useParams();
  const org = orgSlug ?? "acme";

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: {
          width: DRAWER_WIDTH,
          boxSizing: "border-box",
          borderRight: 1,
          borderColor: "divider",
        },
      }}
    >
      <Toolbar variant="dense" />
      <Box sx={{ overflowY: "auto", py: 1 }}>
        <Typography
          variant="overline"
          color="text.secondary"
          sx={{ display: "block", px: 2, pt: 1 }}
        >
          Organisation
        </Typography>
        <List dense>
          {entries
            .filter((e) => e.scope === "org")
            .map((e) => (
              <NavItem key={e.label} entry={e} orgSlug={org} projectSlug={projectSlug} />
            ))}
        </List>
        <Divider sx={{ my: 1 }} />
        <Typography
          variant="overline"
          color="text.secondary"
          sx={{ display: "block", px: 2, pt: 1 }}
        >
          Project
        </Typography>
        <List dense>
          {entries
            .filter((e) => e.scope === "project")
            .map((e) => (
              <NavItem key={e.label} entry={e} orgSlug={org} projectSlug={projectSlug} />
            ))}
        </List>
      </Box>
    </Drawer>
  );
}

function NavItem({
  entry,
  orgSlug,
  projectSlug,
}: {
  entry: NavEntry;
  orgSlug: string;
  projectSlug: string | undefined;
}) {
  const disabled = entry.disabled?.(projectSlug) ?? false;
  if (disabled) {
    return (
      <ListItemButton disabled sx={{ mx: 1, borderRadius: 1 }}>
        <ListItemIcon sx={{ minWidth: 32 }}>{entry.icon}</ListItemIcon>
        <ListItemText primary={entry.label} slotProps={{ primary: { variant: "body2" } }} />
      </ListItemButton>
    );
  }
  const to = entry.to(orgSlug, projectSlug);
  return (
    <ListItemButton
      component={NavLink}
      to={to}
      sx={{
        mx: 1,
        borderRadius: 1,
        "&.active": {
          backgroundColor: "action.selected",
          color: "text.primary",
        },
      }}
    >
      <ListItemIcon sx={{ minWidth: 32 }}>{entry.icon}</ListItemIcon>
      <ListItemText primary={entry.label} slotProps={{ primary: { variant: "body2" } }} />
    </ListItemButton>
  );
}
